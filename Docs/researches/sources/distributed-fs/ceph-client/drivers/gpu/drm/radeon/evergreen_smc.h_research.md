# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_smc.h

## Purpose
`evergreen_smc.h` defines Evergreen System Management Controller firmware table structures and firmware-header offsets used by Radeon power-management code. It extends the RV770 SMC definitions with Evergreen memory-controller register table layouts.

## Important APIs, Types, And Functions
The header includes `rv770_smc.h`, enables one-byte structure packing with `#pragma pack(push, 1)`, and defines `SMC_EVERGREEN_MC_REGISTER_ARRAY_SIZE` as 16. `struct SMC_Evergreen_MCRegisterAddress` stores two 16-bit address selectors (`s0`, `s1`). `struct SMC_Evergreen_MCRegisterSet` stores 16 32-bit register values. `struct SMC_Evergreen_MCRegisters` contains a `last` index byte, three reserved bytes, 16 register-address entries, and five register-value sets. Typedef aliases mirror the struct names. Firmware-header offsets identify `softRegisters`, `stateTable`, and `mcRegisterTable` fields relative to `EVERGREEN_SMC_FIRMWARE_HEADER_LOCATION`.

## Control Flow
There is no executable control flow. The header defines binary layouts that other code uses when parsing, constructing, or uploading SMC firmware tables.

## State And Persistence Behavior
The structures model persistent firmware-facing state rather than storing state themselves. Packing is critical because these structures map directly to SMC firmware memory layout; padding differences would corrupt table interpretation. Values loaded through these layouts persist in SMC-controlled firmware tables and influence memory-clock/power-state behavior.

## Dependencies And Integration Points
The file depends on RV770 base SMC definitions and standard fixed-width integer types supplied through included kernel headers. It integrates with Radeon Evergreen power-management and firmware-loading code that locates the SMC firmware header at `0x100` and follows the table offsets to program memory-controller registers for different power states.

## Risks
Binary layout drift is the main risk. Changing packing, array size, field order, or typedef names can break firmware communication. Offset constants must match the SMC firmware ABI; incorrect offsets can make power-management code read or write the wrong firmware table. Because these tables affect memory-controller setup, mistakes may cause hangs during clock changes or resume.

## Test Signals
Build coverage confirms the header remains syntactically compatible. Runtime signals include successful SMC firmware initialization, stable power-state transitions, memory clock changes without display corruption, suspend/resume stability, and absence of SMC table parsing errors in Radeon debug logs.
