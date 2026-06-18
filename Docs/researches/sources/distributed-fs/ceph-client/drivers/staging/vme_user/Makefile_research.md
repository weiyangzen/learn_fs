## sources/distributed-fs/ceph-client/drivers/staging/vme_user/Makefile

Purpose: this Makefile builds the VME bus framework, userspace access driver, and optional bridge drivers according to Kconfig symbols.

Important definitions: `obj-$(CONFIG_VME_BUS) += vme.o`, `obj-$(CONFIG_VME_USER) += vme_user.o`, `obj-$(CONFIG_VME_TSI148) += vme_tsi148.o`, and `obj-$(CONFIG_VME_FAKE) += vme_fake.o`.

Control flow and state: the build system includes each object based on the matching configuration symbol. Runtime behavior is in the corresponding C files, not here.

Dependencies and integration points: paired with `vme_user/Kconfig` and the staging driver sources in the same directory. `vme.o` provides the core API used by both bridge and userspace drivers.

Risks: object names are simple one-to-one entries; adding new bridge sources requires explicit Makefile and Kconfig updates. Building `vme_user.o` without a functioning bridge may create a module that loads but cannot provide useful access.

Test signals: build matrix for `VME_BUS`, `VME_USER`, `VME_TSI148`, and `VME_FAKE` as built-in and modules; module dependency checks should ensure userspace access links against the framework symbols.
