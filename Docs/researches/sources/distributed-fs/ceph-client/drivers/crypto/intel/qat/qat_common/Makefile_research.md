# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/Makefile

## Purpose
This Kbuild fragment defines the shared `intel_qat` base module. It links the common accelerator framework, firmware loader, transport, algorithm providers, config/control paths, generation helpers, optional debugfs features, optional SR-IOV PF/VF messaging, and optional heartbeat error injection.

## Important APIs, Types, And Functions
The main declaration is `obj-$(CONFIG_CRYPTO_DEV_QAT) += intel_qat.o`. `intel_qat-y` includes core files such as `adf_init.o`, `adf_transport.o`, `adf_admin.o`, `adf_accel_engine.o`, `adf_ctl_drv.o`, crypto/compression algorithm files, HAL/UOF loader, and generation data helpers. Conditional lists add debugfs telemetry/heartbeat files, SR-IOV PF/VF code, and error injection.

## Control Flow
Kbuild assembles different common-module capabilities according to `CONFIG_DEBUG_FS`, `CONFIG_PCI_IOV`, and `CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION`. Runtime module initialization is in `adf_ctl_drv.c`, which creates the control character device and registers crypto/compression services.

## State And Persistence Behavior
No runtime state exists in the Makefile. Its persistent effect is which code is compiled into the common base module and which symbols are exported in the default `CRYPTO_QAT` namespace.

## Dependencies And Integration Points
It integrates all device-specific QAT modules with one shared base module. `ccflags-y` sets the default symbol namespace to `CRYPTO_QAT`, so PF/VF device modules import common exports explicitly.

## Risks
Conditional compilation changes behavior substantially: no debugfs removes diagnostics, no PCI_IOV stubs SR-IOV functions, and missing files can cause unresolved symbols in device modules. The base module also owns algorithm registration, so build composition affects user-visible Crypto API support.

## Test Signals
Build matrix coverage with debugfs on/off, PCI_IOV on/off, and error injection on/off; successful `intel_qat` module load; `/dev/qat_adf_ctl` creation; crypto/compression registrations; and no unresolved namespace imports from device modules.
