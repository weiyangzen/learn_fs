# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/firmware_if.c

## Purpose

`firmware_if.c` implements the common HabanaLabs kernel-driver firmware interface. It covers firmware image acquisition and copying, CPU-CP packet submission, preboot readiness detection, static and dynamic firmware boot protocols, boot-error decoding, hardware-monitor and telemetry requests, PLL/frequency/power operations, secure-attestation requests, and generic CPU-CP passthrough. It is the concrete implementation behind many `hl_fw_*` declarations in `habanalabs.h`, and it relies on ASIC-specific callbacks for queue operations, firmware image placement, PLL index mapping, BAR/register access, and per-ASIC boot-loader initialization.

## Important APIs and Functions

- `hl_fw_version_cmp()` compares parsed firmware SW version fields stored on `struct hl_device` against a caller-supplied version.
- `hl_request_fw()`, `hl_release_firmware()`, `hl_fw_copy_fw_to_device()`, `hl_fw_load_fw_to_device()` wrap Linux firmware loading, validate size/alignment, and copy firmware bytes through MMIO.
- `hl_fw_send_cpu_message()` is the central CPU-CP packet path. It allocates CPU-accessible DMA memory, serializes the CPU queue with `send_cpu_message_lock`, submits a queue BD, polls the packet fence, decodes firmware return codes, scrubs the submitted BD control field, and frees the DMA buffer.
- CPU-CP convenience wrappers include IRQ unmasking, heartbeat/test packets, soft reset, device activity, EEPROM, monitor dump, PCI counters, energy, PLL info, power, DRAM row data, engine-core ASID, signed device info, secure attestation, and generic passthrough.
- `hl_fw_wait_preboot_ready()`, `hl_fw_read_preboot_status()`, and helpers read preboot status/error/capability registers, decide whether the dynamic loader is available, and initialize the proper firmware loader.
- `hl_fw_dynamic_send_protocol_cmd()` implements the dynamic COMMS register protocol: clear status, send command, wait for ACK, clear again, send NOOP, and optionally wait for OK with another clear/NOOP cycle.
- `hl_fw_dynamic_request_descriptor()`, `hl_fw_dynamic_read_and_validate_descriptor()`, and `hl_fw_dynamic_validate_descriptor()` fetch firmware-provided descriptors, validate magic/version/CRC and memory bounds, and record the image destination region.
- `hl_fw_dynamic_init_cpu()` and `hl_fw_static_init_cpu()` are the two high-level boot paths selected by `hl_fw_init_cpu()`.
- `hl_fw_get_frequency()`, `hl_fw_set_frequency()`, `hl_fw_get_clk_rate()`, `hl_fw_get_max_power()`, and `hl_fw_set_max_power()` expose firmware-backed clock and power control.

## Control Flow

Firmware boot starts outside this file with ASIC setup filling `hdev->fw_loader` and `hdev->asic_prop`. `hl_fw_read_preboot_status()` initializes pre-load parameters, waits for preboot, reads preboot capability/status registers, sets `asic_prop.dynamic_fw_load`, calls the ASIC firmware-loader initializer, and reads legacy preboot versions if static loading is required.

`hl_fw_init_cpu()` branches to dynamic or static boot:

- Dynamic boot resets the COMMS state, optionally sends the current reset cause, requests a descriptor, updates reserved FW memory and preboot/binning information when stopping before boot CPU, otherwise loads boot-fit, waits for boot-fit, updates boot-fit state, initializes DRAM scrambling, optionally skips BMC, loads Linux, waits for Linux, updates Linux state, and adjusts interrupt interface compatibility.
- Static boot waits for a boot-fit request, loads boot-fit via ASIC callback when requested, signals readiness via static message registers, waits for boot-loader readiness, reads boot-fit version, updates state, initializes DRAM scrambling, optionally loads Linux through the ASIC callback, handles BMC skip, waits for Linux SRAM availability, reads boot errors, and updates Linux state.

CPU-CP runtime requests mostly construct `struct cpucp_packet`, call `hdev->asic_funcs->send_cpu_message()`, and interpret `result` or DMA-returned buffers. Larger responses use `hl_cpu_accessible_dma_pool_alloc()` and pass the DMA address in the packet.

## State and Persistence Behavior

This file mutates durable per-device kernel state rather than external persistent storage. Important state includes firmware version fields, `hdev->fw_loader.fw_comp_loaded`, dynamic descriptor validity, current dynamic response, image region, image size, boot image properties, timeouts, skip-BMC flag, firmware capability/status fields in `asic_prop`, `device_cpu_disabled`, `device_cpu_is_halted`, heartbeat timestamps, and preboot-provided binning masks. Firmware blobs are requested from the Linux firmware subsystem and released after copying. DMA buffers are allocated from a per-device CPU-accessible gen_pool-backed region and freed after each request.

## Dependencies and Integration Points

The file depends on `habanalabs.h`, `hl_boot_if.h`, CPU-CP interface types, Linux firmware loading, CRC32, vmalloc, PCI helpers, gen_pool, and Habanalabs tracepoints. It calls common helpers such as `hl_hw_queue_submit_bd()`, `hl_hw_queue_inc_ci_kernel()`, `hl_device_operational()`, `hl_build_hwmon_channel_info()`, `hl_get_pci_memory_region()`, and polling/register macros from `habanalabs.h`. Its strongest integration point is `hdev->asic_funcs`, which supplies CPU message transport, firmware image copying, MSI layout, PLL mapping, firmware loader register setup, DRAM scrambling, and binning/property recalculation.

## Risks and Edge Cases

- CPU-CP queue serialization assumes the CPU queue behaves as an effective single-entry synchronous queue.
- `device_cpu_disabled` is set after CPU-CP timeout, causing follow-on calls to fail with `-EAGAIN` until reset.
- Dynamic descriptor validation is security- and stability-sensitive because descriptor addresses drive MMIO copies into SRAM/DRAM BARs.
- Memory-bound checks rely on trusted region selection and sane unsigned address arithmetic.
- Version parsing assumes specific `-fw-`/optional `-rc-` formats and clears version fields on parse failure.
- Static and dynamic boot paths intentionally treat some boot bits as non-fatal warnings depending on masks and flags.
- Compatibility branches for advanced CPU-CP return codes, EQ index checking, dynamic PLL maps, MSI info fallback, and interrupt interface selection must be preserved for older firmware.

## Test Signals

Useful validation signals include successful preboot readiness, correct dynamic/static loader selection, successful descriptor CRC/bounds validation, boot-fit/Linux state transitions, `fw_comp_loaded` bit updates, CPU queue test and heartbeat returning `CPUCP_PACKET_FENCE_VAL`, populated `asic_prop.cpucp_info`, hwmon channel creation, parsed preboot/SW versions, and no boot errors under `boot_error_status_mask`. Negative tests should cover missing/oversized/unaligned firmware, descriptor CRC mismatch, unsupported PLL indices, CPU-CP timeout and advanced return-code handling, invalid version strings, BMC skip timeout, and both boot failure paths.
