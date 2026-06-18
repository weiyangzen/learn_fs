
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/Makefile

## Purpose

This Makefile builds the NXP Amphion VPU composite driver. It aggregates platform probing, core management, mailbox transport, V4L2 mem2mem glue, firmware command/message/RPC handling, i.MX8Q SoC support, Windsor encoder, Malone decoder, color handling, decoder/encoder frontends, and debug support into `amphion-vpu`.

## Important APIs, Types, And Functions

There are no runtime APIs in the Makefile itself. The important build variables are `amphion-vpu-objs`, which lists all object files, and `obj-$(CONFIG_VIDEO_AMPHION_VPU) += amphion-vpu.o`, which binds the composite object to the Kconfig symbol.

The object list includes `vpu_drv.o`, `vpu_core.o`, `vpu_mbox.o`, `vpu_v4l2.o`, `vpu_helpers.o`, `vpu_cmds.o`, `vpu_msgs.o`, `vpu_rpc.o`, `vpu_imx8q.o`, `vpu_windsor.o`, `vpu_malone.o`, `vpu_color.o`, `vdec.o`, `venc.o`, and `vpu_dbg.o`.

## Control Flow

Kbuild first compiles each listed source to an object, links them into `amphion-vpu.o`, and then includes that composite object as built-in or module based on `CONFIG_VIDEO_AMPHION_VPU`.

## State And Persistence

The file has no runtime state. It defines build composition, which persists in generated objects/modules.

## Dependencies And Integration Points

It integrates tightly with `Kconfig`, which supplies the single symbol controlling the whole object set. The ordered object list is the build-time integration map for the Amphion driver subsystems: platform driver, VPU core lifecycle, V4L2, firmware interface, codec engines, and debug.

## Risks

Because all objects are always linked together, missing symbols or build breakage in an encoder, decoder, RPC, or debug file breaks the entire driver. The object list must be kept in sync with source renames and new subsystem files. The double spacing before `vdec.o` is harmless but shows this is a hand-maintained list.

## Test Signals

Build with `CONFIG_VIDEO_AMPHION_VPU=m` and verify a single `amphion-vpu` module contains all listed objects. Build with the symbol disabled and verify none of the objects are linked. Link-time tests should catch missing cross-object symbols between V4L2, command/message, Windsor, Malone, and platform support files.
