# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Makefile

## Purpose
The Venus `Makefile` defines how the driver is split into core, decoder, and encoder kernel objects under `CONFIG_VIDEO_QCOM_VENUS`.

## Important Build Targets
- `venus-core-objs` includes shared driver infrastructure: `core.o`, `helpers.o`, `firmware.o`, `hfi_venus.o`, `hfi_msgs.o`, `hfi_cmds.o`, `hfi.o`, parser/platform/PM/debugfs code, and v6 buffer helpers.
- `venus-dec-objs` builds decoder-specific `vdec.o` and `vdec_ctrls.o`.
- `venus-enc-objs` builds encoder-specific `venc.o` and `venc_ctrls.o`.
- The config adds `venus-core.o`, `venus-dec.o`, and `venus-enc.o` to `obj-*`.

## Control Flow And Integration
The build split matches runtime architecture: `venus-core` owns platform probing, firmware/HFI/PM infrastructure, while decoder and encoder child drivers bind to populated platform devices. `core.c` may create dynamic OF nodes for decoder/encoder, which correspond to the separate object modules.

## State And Persistence
No runtime state. Build inclusion is controlled by Kconfig.

## Risks
- Missing an object from `venus-core-objs` can create unresolved symbols for HFI, PM, parser, debugfs, or platform buffer logic.
- Decoder and encoder objects depend on exported symbols from `venus-core`; build and module load order must keep all three under the same config.

## Test Signals
Kernel build should produce `venus-core`, `venus-dec`, and `venus-enc` objects/modules when the config is enabled. Link-time checks validate symbol availability across the split.
