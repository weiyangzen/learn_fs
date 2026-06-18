# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Makefile

## Purpose
This Makefile defines the object composition for the IPU6 driver modules. It splits common PCI/firmware/DMA/MMU/buttress logic into `intel-ipu6.o` and input-system capture logic into `intel-ipu6-isys.o`.

## Important APIs, types, and functions
`intel-ipu6-y` includes `ipu6.o`, `ipu6-bus.o`, `ipu6-dma.o`, `ipu6-mmu.o`, `ipu6-buttress.o`, `ipu6-cpd.o`, and `ipu6-fw-com.o`. `intel-ipu6-isys-y` includes ISYS core, CSI-2, firmware ABI, video, queue, subdev, and MCD/JSL/DWC PHY implementations. Both modules are controlled by `obj-$(CONFIG_VIDEO_INTEL_IPU6)`.

## Control flow and integration points
The core module provides exported namespace symbols such as CPD parsing, buttress authentication, DMA helpers, and fw-com queues. The ISYS module consumes those symbols for capture pipelines and firmware messaging. This split mirrors runtime topology: PCI core probes the IPU, creates auxiliary devices, and ISYS binds as an auxiliary driver.

## State, persistence, and dependencies
The file has no runtime state but determines link boundaries and symbol visibility. Any source added to IPU6 must be assigned to the correct module or exported/imported symbols will fail.

## Risks and test signals
Risks include omitted objects, wrong module split, namespace/export failures, and init-order assumptions hidden by built-in builds. Test signals are modular and built-in kernel builds, `modpost` without unresolved symbols, module load/unload of `intel_ipu6` and `intel_ipu6_isys`, and probe ordering with auxiliary devices.
