# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/platform.c

## Purpose
`platform.c` registers generic platform devices for Alchemy SoC peripherals: 8250 UARTs, OHCI/EHCI USB hosts, and Au1000 Ethernet MACs. It also provides board override support for Ethernet platform data and power callbacks for USB controllers.

## Important APIs, Types, And Functions
The main init entry is `au1xxx_platform_init()` as an `arch_initcall()`. UART support uses `alchemy_8250_pm()`, `PORT()`, `au1x00_uart_data`, `au1xx0_uart_device`, and `alchemy_setup_uarts()`. USB support uses `alchemy_ehci_power_on/off()`, `alchemy_ohci_power_on/off()`, `alchemy_ehci_pdata`, `alchemy_ohci_pdata`, `alchemy_ohci_data`, `alchemy_ehci_data`, `_new_usbres()`, and `alchemy_setup_usb()`. Ethernet support uses `MAC_RES()`, `au1xxx_eth0_resources`, `au1xxx_eth1_resources`, `au1xxx_eth*_platform_data`, `au1xxx_eth*_device`, `au1xxx_override_eth_cfg()`, and `alchemy_setup_macs()`.

## Control Flow
At arch initcall, CPU type detection drives UART, MAC, and USB setup. UART setup obtains and enables `ALCHEMY_PERIPH_CLK`, copies the CPU-specific port table into allocated platform data, fills `uartclk`, lets `au_platform_setup()` validate/setup each port, and registers one `serial8250` platform device. USB setup registers OHCI0 for every variant, EHCI0 for Au1200/Au1300, and OHCI1 for Au1300, each with memory/IRQ resources and power callbacks that call `alchemy_usb_control()`.

Ethernet setup first checks how many MACs the CPU exposes. It duplicates resource arrays for MAC0/MAC1, optionally fills MAC addresses from PROM `ethaddr`, registers MAC0, then registers MAC1 only if the CPU has a second MAC and the pin function register indicates MAC1 is enabled. Boards can call `au1xxx_override_eth_cfg()` before this initcall to customize PHY search or MAC data.

## State And Persistence
The file persists platform devices, allocated UART platform-data arrays, allocated USB platform_device/resource objects, duplicated Ethernet resource arrays, Ethernet MAC platform data, and USB power state as controlled by host drivers. `alchemy_8250_pm()` changes UART hardware enable state on serial power transitions.

## Dependencies And Integration Points
It depends on common clock framework, serial 8250 platform support, USB OHCI/EHCI platform drivers, Alchemy USB control helpers, PROM Ethernet address parsing, Alchemy CPU capability helpers (`alchemy_get_uarts()`, `alchemy_get_macs()`), and Ethernet platform data headers. Board files such as MTX-1 call `au1xxx_override_eth_cfg()` before this file registers MACs.

## Risks
Init ordering matters: board overrides must run before MAC registration, and clock registration must happen before UART setup. Some allocation failures only log and continue, potentially leaving partial device registration. UART platform data is dynamically allocated and assigned to a static platform device, so failed `au_platform_setup()` frees data and returns without registering UARTs. MAC1 registration depends on `SYS_PF_NI2` polarity, which must match hardware documentation. USB resources use a fixed 0x100 register size and shared DMA mask assumptions.

## Test Signals
Boot all Alchemy CPU types and confirm the expected count of UARTs, USB hosts, and Ethernet MACs. Serial tests should verify baud timing from `ALCHEMY_PERIPH_CLK` and suspend/resume PM enabling/disabling UART blocks. USB tests should bind OHCI/EHCI platform drivers and verify `alchemy_usb_control()` power callbacks. Ethernet tests should confirm PROM MAC parsing, board override application, MAC1 pinfunc gating, resource windows, IRQs, and DMA masks.
