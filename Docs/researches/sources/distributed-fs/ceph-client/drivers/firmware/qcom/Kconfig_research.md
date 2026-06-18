# sources/distributed-fs/ceph-client/drivers/firmware/qcom/Kconfig

## Purpose
This Kconfig file declares the Qualcomm firmware driver menu and the build-time feature relationships for SCM, TrustZone memory allocation, QSEECOM, and the QSEECOM UEFI secure app client.

## Important Symbols
- `QCOM_SCM`: tristate core Secure Channel Manager support. It selects `QCOM_TZMEM`.
- `QCOM_TZMEM`: tristate TrustZone memory allocator support. It selects `GENERIC_ALLOCATOR`.
- `QCOM_TZMEM_MODE_GENERIC`: default allocator mode using page-aligned, non-cacheable, physically contiguous memory.
- `QCOM_TZMEM_MODE_SHMBRIDGE`: allocator mode that also creates Qualcomm Shared Memory Bridge objects; callers must then use TZMem buffers for TrustZone.
- `QCOM_QSEECOM`: bool interface driver for Qualcomm SEE/QSEECOM, depends on built-in `QCOM_SCM=y`, and selects `AUXILIARY_BUS`.
- `QCOM_QSEECOM_UEFISECAPP`: bool EFI-variable client for the QSEE `uefisecapp`, depends on QSEECOM and EFI.

## Control Flow And Integration
The choice block forces exactly one TZMem mode when `QCOM_TZMEM` is enabled. QSEECOM is limited to built-in SCM because it is initialized from SCM's probe path and registers client devices for secure applications. The UEFI secure app client becomes available only when QSEECOM can create auxiliary clients and EFI variable infrastructure exists.

## State And Persistence
There is no runtime state in Kconfig, but these options determine whether SCM and TZMem are modular or built in, whether SHM Bridge behavior is active, and whether EFI variables can be mediated through Qualcomm SEE.

## Risks
Selecting SHM Bridge changes the TrustZone buffer contract system-wide for these drivers and can break callers that pass non-TZMem buffers. The QSEECOM dependency on `QCOM_SCM=y` means modular SCM builds cannot use this interface. Misconfigured EFI/QSEECOM options can leave platforms without efivarfs access.

## Test Signals
Expected build results are `qcom-scm.o` and `qcom_tzmem.o` when SCM is enabled, plus QSEECOM objects when the bools are selected. Runtime logs from `qcom_scm_probe()`, TZMem SHM Bridge enablement, and QSEECOM probing confirm the selected configuration took effect.
