<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h` defines Freescale/NXP SoC USB register offsets, bit masks, and timing constants used by `ehci-fsl.c`. The source was read as a complete 56-line file.

## Important APIs, Types, and Functions

The header has no functions or types. Important constants cover non-EHCI register offsets such as `FSL_SOC_USB_SBUSCFG`, `FSL_SOC_USB_PORTSC1/2`, `FSL_SOC_USB_USBMODE`, `FSL_SOC_USB_USBGENCTRL`, `FSL_SOC_USB_ISIPHYCTRL`, snoop/priority/SI/control registers, PHY/interface bits such as `PORT_PTS_UTMI`, `PORT_PTS_ULPI`, `PORT_PTS_SERIAL`, `PORT_PTS_PTW`, `USBMODE_CM_HOST`, `USBMODE_ES`, `CTRL_UTMI_PHY_EN`, `USB_CTRL_USB_EN`, `ULPI_PHY_CLK_SEL`, `PHY_CLK_VALID`, and `UTMI_PHY_CLK_VALID_CHK_RETRY`.

## Control Flow

There is no executable control flow. The constants parameterize probe, PHY setup, EHCI reset override, and PM restore code in `ehci-fsl.c`.

## State and Persistence Behavior

The header owns no state. Its values describe hardware-visible register state controlled by the Freescale EHCI wrapper.

## Dependencies and Integration Points

It is included by `ehci-fsl.c` and must match the Freescale SoC USB controller register map and platform data semantics from `linux/fsl_devices.h`.

## Risks and Edge Cases

Incorrect bit masks can corrupt SoC control registers, especially write-one-to-clear fields guarded by `CONTROL_REGISTER_W1C_MASK` and big-endian non-EHCI registers. The constants mix standard EHCI-adjacent port fields with Freescale-specific control registers, so changes require hardware documentation review.

## Test Signals

Compile coverage through `ehci-fsl.c`, register write/read traces on Freescale hardware, PHY-mode validation for ULPI/UTMI/serial modes, and suspend/resume register restore checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h -->
