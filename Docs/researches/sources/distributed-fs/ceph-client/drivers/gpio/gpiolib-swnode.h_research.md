# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-swnode.h

## Purpose
`gpiolib-swnode.h` declares the software-node GPIO lookup interface used by generic GPIO consumer code.

## Important APIs, Types, And Functions
It forward-declares `struct fwnode_handle` and `struct gpio_desc`, then declares `swnode_find_gpio()` and `swnode_gpio_count()`.

## Control Flow
Generic firmware lookup code can call these helpers when a consumer fwnode is backed by a software node. The implementation resolves references and counts GPIOs from software-node properties.

## State And Persistence
The header has no state. It defines the internal contract between generic gpiolib lookup and `gpiolib-swnode.c`.

## Dependencies And Integration Points
It integrates software-node property descriptions with the gpiolib consumer API.

## Risks
Signatures must remain aligned with generic gpiolib lookup expectations, particularly native lookup flag output and index handling.

## Test Signals
Build-test software-node GPIO support and run lookup/count tests for software-node-backed consumers.
