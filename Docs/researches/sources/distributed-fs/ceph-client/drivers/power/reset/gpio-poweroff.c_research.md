# sources/distributed-fs/ceph-client/drivers/power/reset/gpio-poweroff.c

## Purpose
generic GPIO-driven poweroff driver.

## Important APIs, Types, and Functions
`struct gpio_poweroff`, `gpio_poweroff_do_poweroff()`, and probe parse GPIO, active/inactive delays, timeout, and priority.

## Control Flow
probe obtains an output GPIO and optional timing properties, then registers a poweroff handler; callback drives active, waits, optionally drives inactive, waits timeout, and warns if still running.

## State and Persistence Behavior
driver stores GPIO descriptor and timings; GPIO output level persists after callback until board power is removed or another consumer changes it.

## Dependencies and Integration Points
OF, gpiod consumer API, sys-off poweroff.

## Risks and Edge Cases
wrong GPIO polarity or timings can hang shutdown; no hardware confirmation other than timeout warning; GPIO shared with another consumer can conflict.

## Test Signals
DT polarity and delay properties, active-low boards, timeout path, and repeated bind/unbind.
