# sources/distributed-fs/ceph-client/net/shaper/Makefile

## Purpose
Builds the generic net shaper infrastructure into the kernel networking core by compiling `shaper.o` and generated netlink glue `shaper_nl_gen.o`.

## Important APIs, Types, And Functions
There are no C APIs in this Makefile. The key build declaration is `obj-y += shaper.o shaper_nl_gen.o`, making the infrastructure built-in rather than conditional on a visible Kconfig symbol in this directory.

## Control Flow
Kbuild includes both the hand-written shaper implementation and generated YNL netlink family implementation whenever this directory participates in the network build.

## State And Persistence
No runtime state. It controls object inclusion in the built kernel.

## Dependencies And Integration Points
Depends on Kbuild traversal from the parent networking Makefile. It integrates generated code with the hand-written implementation, so missing either object breaks `net_shaper_nl_family` registration or operation callbacks.

## Risks
Risks are build-only: unconditional inclusion can expose missing dependencies on headers or symbols, and generated/hand-written files must remain in sync with `Documentation/netlink/specs/net_shaper.yaml`.

## Test Signals
Build-test networking configurations, confirm both objects appear in the link, and run netlink family registration tests to catch missing generated callback symbols.
