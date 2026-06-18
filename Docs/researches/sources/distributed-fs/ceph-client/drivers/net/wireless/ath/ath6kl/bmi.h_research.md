# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.h

Purpose: Documents and declares the ath6kl Bootloader Messaging Interface protocol, command IDs, target-info structure, HI-item helpers, and BMI function prototypes.

Important APIs and definitions: Command IDs include `BMI_DONE`, `BMI_READ_MEMORY`, `BMI_WRITE_MEMORY`, `BMI_EXECUTE`, `BMI_SET_APP_START`, SOC register read/write, target info, ROM patch commands, and LZ stream/data. `TARGET_VERSION_SENTINAL`, `TARGET_TYPE_AR6003`, and `TARGET_TYPE_AR6004` identify target-info behavior. `struct ath6kl_bmi_target_info` is a packed little-endian byte-count/version/type response. Macros `ath6kl_bmi_write_hi32()` and `ath6kl_bmi_read_hi32()` resolve host-interest item addresses and perform little-endian 32-bit BMI access.

Control flow: The comments define request/response payload formats used by `bmi.c`. The HI helper macros call `ath6kl_get_hi_item_addr()`, then perform BMI memory reads/writes for firmware boot-time configuration.

State and persistence: No state is owned in the header. It defines the protocol that mutates target bootloader memory/register state before firmware starts. `BMI_DONE` marks the end of the bootloader access window.

Dependencies and integration points: Depends on `struct ath6kl`, target HI item address lookup, little-endian conversion helpers, and implementations in `bmi.c`. Integrated with firmware download, board/OTP/patch setup, and target bootstrapping.

Risks: Command IDs and struct layout are firmware ABI; changes must remain target-ROM compatible. The misspelled `TARGET_VERSION_SENTINAL` is part of local API spelling and should not be casually renamed. HI helper macros evaluate arguments in expression context and rely on pointer type checking tricks.

Test signals: Compile BMI users, validate packed struct size, read/write HI items on target boot, handle old and new target-info responses, and ensure every declared command prototype links to `bmi.c`.
