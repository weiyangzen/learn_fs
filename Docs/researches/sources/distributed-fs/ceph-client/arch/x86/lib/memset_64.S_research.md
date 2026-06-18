# sources/distributed-fs/ceph-client/arch/x86/lib/memset_64.S

Purpose: implements 64-bit `memset`/`__memset` in noinstr text with fast-string alternatives and manual fallback.

Important APIs/functions: exports `__memset`, aliases/exports `memset`, and defines local `memset_orig`.

Control flow: if `X86_FEATURE_FSRS` is available, `__memset` saves destination in `%r9`, expands byte into `%al`, runs `rep stosb`, returns original destination in `%rax`. Fallback expands the byte across a qword, handles initial unaligned destination by one unaligned qword store when length permits, writes 64-byte chunks with eight qword stores, then 8-byte and byte tails.

State and persistence behavior: fills destination memory with a byte pattern and returns original destination. No globals.

Dependencies/integration points: core kernel memory API, x86 alternatives, CFI annotations, noinstr constraints, and exported module symbols.

Risks: fallback unaligned qword store intentionally writes within the requested range only when enough bytes exist; alignment math must remain correct. Fast-string alternative must preserve return value. No instrumentation is allowed in noinstr text.

Test signals: memset correctness across lengths 0-128 and alignments, large fills, FSRS and fallback CPU paths, objtool noinstr validation, and KASAN/KMSAN tests.
