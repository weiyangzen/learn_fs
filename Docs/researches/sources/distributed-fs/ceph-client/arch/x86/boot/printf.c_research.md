# sources/distributed-fs/ceph-client/arch/x86/boot/printf.c

Purpose: provides small boot-time formatting functions for diagnostics without full libc or kernel printf.

Important APIs and state: defines `vsprintf()`, `sprintf()`, and `printf()`. Helpers `skip_atoi()` and `number()` implement integer formatting. `printf()` uses a fixed 1024-byte stack buffer and writes through `puts()`.

Control flow: parser supports flags, width, precision, `h/l/L` qualifiers, `%c`, `%s`, `%p`, `%n`, `%%`, and integer formats in bases 8/10/16. It explicitly lacks full 64-bit formatting support beyond `unsigned long`.

Dependencies and integration: used by CPU, EDD, video, and diagnostic paths. Depends on boot `ctype.h`, `strnlen()`, and `tty.c`.

Risks and test signals: no bounds checking on the output buffer means long formatted output can overflow. Test normal boot diagnostics, missing CPU features, video menu output, and format cases used by setup code.
