# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/Kconfig

Purpose: defines Kconfig options for the STMicroelectronics HVA hardware video encoder V4L2 driver and optional debugfs support.

Important APIs and symbols: `VIDEO_STI_HVA` is the user-visible tristate, depending on V4L mem2mem drivers, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`, and selecting `VIDEOBUF2_DMA_CONTIG` plus `V4L2_MEM2MEM_DEV`. `VIDEO_STI_HVA_DEBUGFS` is a bool child option depending on `VIDEO_STI_HVA` and `DEBUG_FS`.

Control flow: selected symbols determine whether `st-hva` is built and whether `hva-debugfs.o` is included.

State and persistence: no runtime state. Values persist in the kernel build configuration and affect module capabilities.

Dependencies and integration points: integrates with the media platform encoder tree, videobuf2, V4L2 mem2mem, STi architecture support, and debugfs.

Risks: debugfs is optional and should not be assumed by diagnostics. The driver help calls HVA multi-format, but this subset only provides H.264 encoders for NV12/NV21 input through `hva-h264.c`.

Test signals: menuconfig visibility, `COMPILE_TEST`, module builds with debugfs on/off, and boot-time probe on STi hardware.
