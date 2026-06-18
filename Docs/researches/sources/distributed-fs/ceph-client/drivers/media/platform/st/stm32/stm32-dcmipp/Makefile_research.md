# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/Makefile

Purpose: declares the object composition for the STM32 DCMIPP driver module.

Important build rule: `stm32-dcmipp-y` links `dcmipp-core.o`, `dcmipp-common.o`, `dcmipp-input.o`, `dcmipp-byteproc.o`, and `dcmipp-bytecap.o` into one `stm32-dcmipp.o` module when `CONFIG_VIDEO_STM32_DCMIPP` is enabled.

Control flow and integration: kbuild uses this file after the parent STM32 Makefile descends into the directory. The composition mirrors the runtime pipeline: core platform/media orchestration, common entity helpers, input bridge, byte processor, and byte capture node.

State and risks: no runtime state. Risks are missing new DCMIPP entity objects from the aggregate list or breaking link order assumptions for init/release symbols. Test signals are modular and built-in builds of `CONFIG_VIDEO_STM32_DCMIPP`, plus symbol resolution for all `dcmipp_*_ent_init` and release functions.
