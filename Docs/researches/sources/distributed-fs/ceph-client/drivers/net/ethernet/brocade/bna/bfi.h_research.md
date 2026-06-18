# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfi.h

## Purpose
`bfi.h` defines the common Brocade/QLogic Firmware Interface ABI shared by IOC, MSGQ, flash, and other message classes. It contains packed firmware message headers, DMA address layouts, message class IDs, IOC firmware image/version/state formats, MSGQ mailbox formats, and flash request/response formats.

## Important APIs, Types, and Functions
- `struct bfi_mhdr` is the common mailbox header, with `msg_class`, `msg_id`, and a union for host-to-firmware function/LPU routing or firmware-to-host token.
- `bfi_h2i_set()` and `bfi_i2h_set()` fill common mailbox headers.
- `BFA_I2HM()` maps host-to-firmware opcode numbers into firmware-to-host opcode space using `BFI_I2H_OPCODE_BASE`.
- `union bfi_addr_u` and `struct bfi_alen` define firmware-visible DMA address and address-length payloads.
- `enum bfi_mclass` assigns class numbers, including `BFI_MC_IOC`, `BFI_MC_FLASH`, `BFI_MC_CEE`, `BFI_MC_MSGQ`, and `BFI_MC_ENET`.
- IOC definitions include ASIC generation/mode enums, IOC control/getattr messages, firmware image header/version structures, firmware boot modes, heartbeat, and `enum bfi_ioc_state`.
- MSGQ definitions include mailbox init/doorbell/copy opcodes, `struct bfi_msgq_mhdr`, queue configuration structures, and copy-request/response structures.
- Flash definitions include query, erase, write, read, boot-version opcodes, and request/response payloads.

## Control Flow and State
This header is declarative, but it determines runtime control flow across the driver. IOC enable/disable/getattr messages use `struct bfi_ioc_ctrl_req`, `struct bfi_ioc_getattr_req`, and matching replies. MSGQ initialization uses `struct bfi_msgq_cfg_req` to hand firmware the DMA rings, then doorbell structures move producer/consumer indices. ENET commands use the MSGQ-specific `struct bfi_msgq_mhdr`, whose `num_entries` determines how many 64-byte queue entries a command or response consumes.

## State and Persistence Behavior
The structures describe firmware-visible state held in DMA memory, mailbox registers, or firmware memory. `struct bfi_ioc_image_hdr` and `struct bfi_ioc_fwver` are used to compare running firmware to the driver image. `enum bfi_ioc_state` values are written into hardware state registers by `bfa_ioc_ct.c` and interpreted by the common IOC state machine.

## Dependencies and Integration Points
`bfi.h` includes `bfa_defs.h` and is included by most files in this work item. `bfa_ioc_ct.c` uses IOC state, firmware header, ASIC mode/generation, and SRAM offsets. `bfa_msgq.c` uses MSGQ mailbox and ring formats. `bfi_cna.h` and `bfi_enet.h` layer class-specific message formats on top of these common headers.

## Risks
- Almost every structure is `__packed` and hardware ABI-sensitive; padding, field order, endian, or size changes can break firmware communication.
- `bfi_msgq_mhdr_set()` does not set `num_entries`; each caller must do so correctly.
- Some fields are host endian while many firmware payloads require big-endian conversions by callers.
- `BFI_MC_MAX` bounds response-handler arrays; adding classes must keep handler users in sync.
- Firmware image comparison and IOC state values affect multi-function firmware ownership and recovery.

## Test Signals
Useful signals include compile-time structure-size expectations, successful IOC enable/getattr/heartbeat handling, MSGQ init and doorbells, ENET responses arriving with expected opcodes, flash query/read/write operations, and firmware-version mismatch detection in `bfa_ioc_ct_firmware_lock()`.
