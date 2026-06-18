# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-berr.c

Purpose: IP27 HUB bus-error handling. It decodes HUB error status registers for the local slice and installs the MIPS bus-error handler.

Important APIs and control flow: `dump_hub_information()` parses `PI_ERR_STATUS0/1` into address, command, supplemental field, RRB request, overrun, and error type. `ip27_be_handler()` allows exception-table fixups, otherwise logs slice, instruction/data type, pending error bits, dumps HUB information, registers, and TLBs, then loops forever before the unreachable SIGBUS path. `ip27_be_init()` installs the handler, clears pending errors, disables error stack, and enables SYSAD checks.

State, persistence, and integration: state is HUB error control registers and the global MIPS BE handler. Dependencies include local HUB access macros and `ip27-common.h` setup. Risks include fatal infinite loop on non-fixup errors, limited Bridge error initialization, and direct HUB register assumptions. Test signals are handler installation, successful fixup on safe probing, and detailed HUB logs on injected errors.
