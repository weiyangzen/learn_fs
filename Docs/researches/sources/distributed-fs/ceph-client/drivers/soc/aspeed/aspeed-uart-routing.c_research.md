# sources/distributed-fs/ceph-client/drivers/soc/aspeed/aspeed-uart-routing.c

## Purpose
This driver exposes ASPEED UART routing muxes through sysfs so users can select UART RX/TX path connections among UART controllers and I/O pins at runtime.

## Important APIs, Types, And Functions
`struct aspeed_uart_routing` stores the parent syscon regmap and selected attribute group. `struct aspeed_uart_routing_selector` binds a sysfs attribute to a register, mask, shift, and option string array. `aspeed_uart_routing_show()` displays current option with brackets. `aspeed_uart_routing_store()` validates and writes a selected option.

## Control Flow
Static selector tables describe AST2500 and AST2600 routing choices. Probe gets the parent regmap, selects an attribute group from match data, creates the sysfs group, and stores driver data. Reads decode the selector field and print all choices. Writes match the provided string against the options array and update the relevant register bits.

## State, Persistence, And Dependencies
State is the hardware routing registers and sysfs attributes. Dependencies include platform device, parent syscon/regmap, OF match data, and sysfs device attributes.

## Integration Points
Userspace configures routes through attributes named like `io1`, `uart1`, and `uart10`. The driver binds to ASPEED UART-routing child nodes for AST2400/2500/2600.

## Risks
`dev_set_drvdata()` is called after `sysfs_create_group()`, so a very early sysfs read could see NULL drvdata. Reserved options are exposed as selectable strings where present. There is no higher-level validation to prevent conflicting routes. Remove uses `platform_get_drvdata()` even though probe used `dev_set_drvdata()`, which is equivalent for platform devices but worth noting.

## Test Signals
Read every sysfs attribute, write all valid options, reject invalid strings, verify register fields, test AST2500 and AST2600 groups, and stress concurrent sysfs writes.
