# sources/distributed-fs/ceph-client/drivers/bus/ti-pwmss.c

## Purpose
This TI AM33xx PWM subsystem wrapper enables runtime PM for the PWMSS bus node and populates its child PWM/eCAP/eQEP-style devices.

## Important APIs, Types, and Functions
`pwmss_probe()` enables runtime PM and calls `of_platform_populate()` on the node. `pwmss_remove()` disables runtime PM. The OF match table contains `ti,am33xx-pwmss`.

## Control Flow
Probe has a simple two-step sequence: enable PM, then populate all child nodes. If child population fails it logs an error and returns the failure, but runtime PM remains enabled because there is no local unwind before returning.

## State and Persistence
There is no driver-private state and no direct MMIO access. Persistent state is runtime PM enablement for the parent bus while bound.

## Dependencies and Integration Points
It depends on OF platform population and runtime PM. It is a parent bus driver for TI PWM subsystem child devices.

## Risks and Test Signals
Risks include missing runtime PM disable on `of_platform_populate()` failure and no explicit child depopulation on remove. Test signals include child device probing, runtime PM enable/disable balance, and correct behavior when no child node is present.
