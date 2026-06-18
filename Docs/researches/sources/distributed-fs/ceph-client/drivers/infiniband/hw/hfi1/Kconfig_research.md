<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig

## Purpose

This Kconfig file declares the HFI1 low-level InfiniBand/RDMA driver option and two debug-oriented configuration switches. The driver is presented as "Cornelis OPX Gen1 support" and can be built as a module or built in.

## Important APIs, types, and functions

The primary symbol is `CONFIG_INFINIBAND_HFI1`. It depends on `X86_64`, `INFINIBAND_RDMAVT`, `I2C`, and `!UML`, and selects `MMU_NOTIFIER`, `CRC32`, and `I2C_ALGOBIT`. `CONFIG_HFI1_DEBUG_SDMA_ORDER` enables SDMA completion ordering debug support for unit testing. `CONFIG_SDMA_VERBOSITY` enables verbose SDMA debug output.

## Control Flow

Kconfig resolution determines whether `drivers/infiniband/hw/hfi1/Makefile` contributes `hfi1.o` to the kernel build. The selected helper symbols ensure required subsystems are available before compiling the driver. The two debug booleans only become visible when `INFINIBAND_HFI1` is enabled.

## State and Persistence

Kconfig selections persist in the kernel `.config`, not in runtime driver state. The debug symbols may compile additional code paths or logging behavior into the resulting HFI1 object, depending on references in other source files.

## Dependencies and Integration Points

The driver integrates with RDMAVT, I2C, MMU notifier, CRC32, and bit-banged I2C infrastructure. The `!UML` exclusion prevents builds for User Mode Linux. X86_64 is required, reflecting platform and hardware assumptions in the HFI1 driver.

## Risks

Dependency changes can break allmodconfig or unsupported architecture builds. Removing selected symbols can produce link or runtime failures in memory registration, CRC, or QSFP/I2C paths. Debug options should remain default-off because they can increase logging volume or alter test-only SDMA behavior.

## Test Signals

Signals are Kconfig visibility checks, `olddefconfig` stability, `CONFIG_INFINIBAND_HFI1=m` and `=y` builds, allmodconfig coverage on x86_64, and negative coverage that UML does not offer the driver. Debug symbols should be build-tested both disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig -->
