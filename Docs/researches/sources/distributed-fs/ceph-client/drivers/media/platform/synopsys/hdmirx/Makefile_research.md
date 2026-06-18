# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Makefile

## Purpose
Builds the Synopsys HDMI receiver as a composite kernel object.

## Important APIs, Types, And Functions
`synopsys-hdmirx-objs` combines `snps_hdmirx.o` and `snps_hdmirx_cec.o`. `obj-$(CONFIG_VIDEO_SYNOPSYS_HDMIRX)` emits the final `synopsys-hdmirx.o` object when the Kconfig symbol is enabled.

## Control Flow
There is no runtime flow. Kbuild compiles both main capture/HDMI logic and the CEC helper into one module/builtin unit.

## State And Persistence
No runtime state. The only persistent effect is the selected kernel build artifact.

## Dependencies And Integration Points
Depends on the local Kconfig symbol and Kbuild object-composition conventions. The CEC implementation is inseparable from the main module from a build perspective.

## Risks
Any compile failure in CEC support prevents the whole HDMI receiver driver from building. There is no conditional object split for CEC despite `CEC_CORE` being selected by Kconfig.

## Test Signals
Kernel builds for `CONFIG_VIDEO_SYNOPSYS_HDMIRX=m` and `=y` should produce the expected module/object and include both source files in dependency output.
