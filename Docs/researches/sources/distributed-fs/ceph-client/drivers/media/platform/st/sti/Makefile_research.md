# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Makefile

Purpose: descends into STI media driver build directories.

Important APIs and entries: unconditionally adds `bdisp/`, `delta/`, `hva/`, and `stm32/` to `obj-y`.

Control flow: kbuild evaluates child Makefiles, which conditionally build objects based on their Kconfig symbols.

State and persistence: no runtime state. Build traversal is the only effect.

Dependencies and integration points: integrates STI media subdrivers with kbuild. The `stm32/` child entry is notable because STM32 is also referenced from the parent ST Makefile, so tree layout should be checked in the full source context.

Risks: adding `stm32/` under `sti/` can fail if that relative directory does not exist in this source tree, depending on kbuild traversal behavior. Unconditional descent requires children to be disabled-clean.

Test signals: `make M=drivers/media/platform/st/sti` and full media builds with all ST drivers disabled and enabled.
