# sources/distributed-fs/ceph-client/drivers/scsi/ips.h

## Purpose

`ips.h` is the shared hardware, firmware, command, status, ioctl, and in-memory object contract for the Adaptec/IBM ServeRAID `ips` SCSI RAID controller driver. It does not implement request execution itself; instead it defines the constants, packet layouts, host-adapter state, queue structures, and function-pointer table consumed by the corresponding driver implementation. The file covers several controller families, including Copperhead/Trombone/Clarinet, Morpheus, and Marco, with macros that decide whether the implementation should use I2O delivery, memory-mapped I/O, or enhanced scatter-gather lists.

## Important APIs, Types, and Functions

The primary access macros are `IPS_HA()`, `IPS_COMMAND_ID()`, `IPS_IS_TROMBONE()`, `IPS_IS_CLARINET()`, `IPS_IS_MORPHEUS()`, `IPS_IS_MARCO()`, `IPS_USE_I2O_DELIVER()`, `IPS_USE_MEMIO()`, `IPS_HAS_ENH_SGLIST()`, `IPS_USE_ENH_SGLIST()`, and `IPS_SGLIST_SIZE()`. Hardware definitions include register offsets such as `IPS_REG_HISR`, `IPS_REG_CCSAR`, `IPS_REG_CCCR`, status queue registers, flash registers, I2O queue registers, and i960 message registers, plus bit definitions for interrupts, queue state, reset, bus mastering, and command start.

Command opcodes include logical-drive information, subsystem reads, configuration reads, NVRAM access, logical read/write, scatter-gather read/write, DCDB passthrough, flush, error table, firmware/BIOS download, version query, FFDC, and channel reset. Packet formats are represented by `IPS_IO_CMD`, `IPS_LD_CMD`, `IPS_IOCTL_CMD`, `IPS_DCDB_CMD`, `IPS_CS_CMD`, `IPS_US_CMD`, `IPS_FC_CMD`, `IPS_STATUS_CMD`, `IPS_NVRAM_CMD`, `IPS_VERSION_INFO`, `IPS_FFDC_CMD`, `IPS_FLASHFW_CMD`, `IPS_FLASHBIOS_CMD`, and the `IPS_HOST_COMMAND` union. Runtime structures include `IPS_ADAPTER` for the status queue, `IPS_LD_INFO`, `IPS_ENQ`, `IPS_CONF`, `IPS_NVRAM_P5`, `IPS_VERSION_DATA`, SCSI inquiry/capacity/sense/mode-page structures, `IPS_STD_SG_LIST`, `IPS_ENH_SG_LIST`, `ips_scb_t`, `ips_scb_pt_t`, and `ips_passthru_t`.

The central software state object is `ips_ha_t`. It owns adapter identity, queue limits, DMA/coherent buffers, SCB freelist/waitlist/activelist, pending passthrough queue, inquiry/config/NVRAM/subsystem buffers, ioctl and flash buffers, MMIO pointers, hardware function table, PCI device pointer, reset/active/wait flags, version data, and compatibility state. `ips_hw_func_t` abstracts controller-specific operations such as reset, issue, init, interrupt detection, interrupt handling, status update, BIOS erase/program/verify, and interrupt enable.

## Control Flow

The header encodes how the implementation is expected to branch during probe and I/O setup. PCI vendor/device/revision and optional module flags drive the chosen register interface and command delivery path. Older adapters use standard 32-bit scatter-gather entries, while Morpheus/Marco or hosts with `IPS_HA_ENH_SG` use enhanced entries with high and low address words. Command construction chooses the packet variant by firmware operation: logical-drive I/O uses `IPS_IO_CMD`; non-disk SCSI passthrough uses `IPS_DCDB_CMD` plus `IPS_DCDB_TABLE`; flash and version paths use their dedicated command structures.

Status flow is built around `IPS_STATUS` entries in an `IPS_ADAPTER` status queue. The implementation can derive command IDs, basic status, and extended status from each status word, then map the command ID back into `ips_ha_t.scbs`. Higher-level SCSI emulation uses the inquiry, read-capacity, request-sense, and mode-page layouts in this header to synthesize or parse target-visible responses.

## State and Persistence Behavior

All driver-owned state is transient kernel memory. Persistent controller state is represented indirectly through NVRAM page 5 (`IPS_NVRAM_P5`), subsystem parameters, firmware/BIOS version records, logical-drive configuration, and flash command packets. The header defines compatibility strings and the `IPS_DEFINE_COMPAT_TABLE()` macro so the implementation can compare adapter type and BIOS/firmware compatibility IDs. `ips_ha_t` tracks reset count, last FFDC timestamp, BIOS version, and `requires_esl`, but those fields are runtime reflections of hardware or policy rather than filesystem persistence.

## Dependencies and Integration Points

The header depends on Linux SCSI, gendisk geometry, DMA address, PCI, MMIO, uaccess, and NMI watchdog support. It is the ABI boundary for user passthrough ioctls such as `IPS_COPPUSRCMD`, `IPS_COPPIOCCMD`, `IPS_NUMCTRLS`, and `IPS_CTRLINFO`; these expose controller commands and adapter information to management utilities. It also integrates with firmware through fixed packet layouts, status codes, version/compatibility IDs, flash image directions, NVRAM signatures, and ServeRAID-specific logical-drive metadata.

## Risks and Edge Cases

Many structures are hardware ABI layouts; field order, width, and alignment are critical. The header mixes 32-bit bus-address fields with `dma_addr_t` fields, so 64-bit DMA paths must consistently select enhanced SGLs and avoid truncation. Several packet structures use fixed 12-byte CDBs while tape/extended variants carry 16-byte CDBs, which is a common source of passthrough errors. `IPS_MAX_*` constants constrain queue depth, logical drives, targets, chunks, and transfer length; implementation code must reject or split requests that exceed them. The compatibility/version block is intentionally generated by build tooling, so manual edits can desynchronize reported driver versions from firmware compatibility checks.

## Test Signals

Useful validation signals include compiling the `ips` driver with no structure-size or prototype drift, probe paths selecting expected IO/MMIO/I2O/enhanced-SG modes for each adapter family, passthrough utilities receiving correctly shaped `ips_passthru_t` data, management queries returning version and compatibility IDs, logical-drive inquiry/capacity/mode-page responses matching the header layouts, and stress I/O over both standard and enhanced scatter-gather paths.
