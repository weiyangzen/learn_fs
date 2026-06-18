# sources/distributed-fs/ceph-client/arch/x86/boot/ctype.h

Purpose: supplies tiny boot-local character classification helpers.

Important APIs and state: inline `isdigit()` and `isxdigit()` only. No state.

Control flow: simple range checks for decimal and hexadecimal characters.

Dependencies and integration: used by early string parsing and printf field-width parsing where libc is unavailable.

Risks and test signals: only ASCII digits/hex letters are supported, which is correct for boot command-line parsing. Test through numeric command-line options and string conversion helpers.
