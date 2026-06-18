# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/Kconfig

Purpose: Kconfig entry for the Aspeed virtual hub USB gadget controller driver.

Important APIs, types, and functions: defines `USB_ASPEED_VHUB` as a tristate "Aspeed vHub UDC driver", depending on `ARCH_ASPEED || COMPILE_TEST` and `USB_LIBCOMPOSITE`.

Control flow: when selected, the parent UDC Makefile descends into `aspeed-vhub/` and builds the virtual hub controller module/object.

State and persistence: selected Kconfig state controls build inclusion only.

Dependencies and integration points: integrates with Aspeed SoC device-tree platform support and libcomposite. The help text documents AST2400, AST2500, and AST2600 vHub USB2.0 functionality.

Risks: the dependency on `USB_LIBCOMPOSITE` means builds without libcomposite cannot enable this UDC, which is appropriate because it registers multiple gadget UDCs. Help text may need updates as newer compatibles such as AST2700 are supported in code.

Test signals: select as built-in and module on ARCH_ASPEED and COMPILE_TEST builds, verify Makefile object inclusion, and confirm device-tree compatible tables probe the driver.
