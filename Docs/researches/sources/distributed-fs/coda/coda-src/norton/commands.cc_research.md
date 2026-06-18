# sources/distributed-fs/coda/coda-src/norton/commands.cc

Purpose: defines the interactive Norton command tree and generic commands for help, memory examination, debug display/set, and unimplemented command stubs.

APIs and flow: command arrays wire parser tokens to handlers for delete/create/list/rename/show/set/examine. `InitParsing` initializes the prompt. `examine` validates an address/length, checks readable memory through platform-specific `address_ok`, then prints hex and ASCII lines. `set_debug`/`show_debug` manipulate global `norton_debug`.

Dependencies and risks: integrates with `parser.h`, platform VM APIs or `mprotect`, and handlers declared in `norton.h`. The Linux `address_ok` uses `mprotect`, which changes page protection and returns zero on success; the calling condition treats zero as failure, so behavior is platform-sensitive. `notyet` uses a fixed 80-byte buffer with repeated `strcat`. Test signal is interactive parser use.
