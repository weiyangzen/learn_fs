# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_cmd.c

## Purpose

`hclge_comm_cmd.c` implements the shared PF/VF command queue transport used to communicate with HNS3 firmware. It allocates coherent descriptor rings, programs command queue registers, submits synchronous command descriptors, waits for firmware writeback, converts firmware return codes to Linux errors, queries firmware version/capabilities, enables firmware compatibility features, and tears command queues down.

## Important Functions

- `hclge_comm_cmd_init_regs()` and internal `hclge_comm_cmd_config_regs()` write CSQ/CRQ DMA base, depth, head, and tail registers.
- `hclge_comm_cmd_setup_basic_desc()` zeroes and initializes command descriptors with opcode, `NO_INTR`, `IN`, and optional read/writeback flag.
- `hclge_comm_cmd_reuse_desc()` prepares an existing descriptor for reuse.
- `hclge_comm_firmware_compat_config()` sends `HCLGE_OPC_IMP_COMPAT_CFG` to enable or disable firmware compatibility feature bits.
- `hclge_comm_alloc_cmd_queue()` and internal allocation/free helpers manage coherent descriptor memory.
- `hclge_comm_cmd_query_version_and_capability()` sends `HCLGE_OPC_QUERY_FW_VER`, stores firmware version, derives device version from hardware version plus PCI revision, and populates `ae_dev->caps`.
- `hclge_comm_cmd_send()` is the main synchronized submission path.
- `hclge_comm_cmd_uninit()`, `hclge_comm_cmd_queue_init()`, and `hclge_comm_cmd_init()` implement lifecycle.
- `hclge_comm_cmd_init_ops()` installs optional trace callbacks.

## Control Flow

Initialization first sets ring locks, descriptor counts, timeout, and coherent CSQ/CRQ memory in `hclge_comm_cmd_queue_init()`. `hclge_comm_cmd_init()` resets software indices, programs hardware registers, clears `HCLGE_COMM_STATE_CMD_DISABLE`, checks pending reset state, queries version/capabilities, logs the firmware version, and attempts compatibility enablement when supported by PF/V3+ requirements.

Command submission in `hclge_comm_cmd_send()` traces outgoing descriptors, takes the CSQ lock, rejects disabled command queues, checks ring space, snapshots the descriptor position for writeback, copies descriptors into the CSQ ring, rings the hardware tail register, waits for completion when the descriptor requests sync behavior, copies firmware-updated descriptors back, converts firmware status to `errno`, cleans the software head from the hardware head register, releases the lock, and traces returned descriptors.

Teardown disables firmware compatibility, sets command disable state, waits for in-flight firmware work, clears hardware registers under CSQ/CRQ locks, and frees both rings.

## State and Persistence Behavior

State lives in `struct hclge_comm_hw::cmq` and `comm_state`: DMA descriptor memory, ring head/tail indices, descriptor counts, timeout, last firmware status, trace callbacks, and disable bit. Firmware-derived capabilities persist in `hnae3_ae_dev::caps` until reset or device teardown. Command descriptor rings are coherent DMA memory and are freed during uninit. There is no filesystem persistence.

## Dependencies and Integration Points

This module depends on `hnae3.h` bitfield helpers and capability definitions, command opcodes and ring structures from `hclge_comm_cmd.h`, PCI DMA APIs, MMIO register accessors, spinlocks, and firmware-visible descriptor formats. It is a foundation for common RSS, TQP stats, MAC, DCB, reset, register dump, and PF/VF backend code that sends admin commands.

## Risks and Edge Cases

- `hclge_comm_cmd_csq_clean()` disables future commands if the hardware head is outside the expected software window, expecting firmware watchdog recovery.
- `hclge_comm_cmd_send()` returns `-EBUSY` when disabled or full; higher layers must retry or fail gracefully.
- Completion waits are polling microsecond loops; long reset commands require the special timeout map.
- Multi-descriptor "special opcodes" take return status from descriptor zero, while normal commands use the last descriptor.
- Capability defaults for V2 devices differ from parsed capabilities for newer devices.
- Firmware compatibility enable failures are warnings after init, so callers must tolerate features not being enabled.

## Test Signals

Strong signals include successful command queue allocation/free under probe/remove, firmware version log output, valid capability bits for PF and VF devices, command timeout behavior for reset trigger commands, clean `-errno` conversion for firmware errors, no command submission after disable, trace callbacks seeing both send and completion descriptors, and reset paths reinitializing indices and registers without leaking DMA memory.
