# sources/distributed-fs/ceph-client/net/strparser/Kconfig

Purpose: Defines the kernel configuration symbol controlling compilation of the stream parser module.

Important APIs/types/functions: `config STREAM_PARSER` is a boolean with `def_bool n`; it is normally selected by consumers rather than prompted directly.

Control flow: Kconfig evaluation leaves stream parser disabled unless another feature selects or enables `STREAM_PARSER`. The Makefile then compiles `strparser.o` only when this symbol is set.

State and persistence behavior: No runtime state exists. The symbol persists only in the kernel build configuration.

Dependencies and integration points: Integrates with `net/strparser/Makefile` and consumers such as TLS/KCM/BPF stream parser users that require framed stream parsing.

Risks and test signals: Risk is missing selection by a consumer, causing link failures or unavailable stream parsing. Test relevant configurations with consumers enabled and disabled, and verify `strparser.o` appears only when expected.
