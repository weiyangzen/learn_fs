# sources/distributed-fs/ceph-client/net/phonet/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_PHONET`, the tristate option for the Nokia Phonet protocol family. It controls compilation of the core Phonet stack and the Phonet pipe endpoint module.

## Important APIs, types, and functions
There are no C APIs in this file. The important interface is the `PHONET` symbol, user-visible prompt, help text, and module naming note. When enabled as a module, the core module is called `phonet`.

## Control flow and state
Kconfig selection determines whether `net/phonet/Makefile` builds `phonet.o` and `pn_pep.o`. There is no runtime state.

## Dependencies and integration points
The option is standalone in this file and is consumed by the Makefile and by C code guarded through the kernel configuration. It enables a protocol stack used for Nokia modem/phone communication and Maemo cellular data support.

## Risks and edge cases
The main risk is configuration discoverability and dependency accuracy. Because this protocol is specialized and security-sensitive, accidentally enabling it broadens kernel attack surface through PF_PHONET sockets and rtnetlink controls. Missing dependencies would surface as build failures.

## Test signals
Build matrix coverage should include `CONFIG_PHONET=n`, `m`, and `y`, verifying that socket family registration, module aliases, and dependent objects are present only when expected.
