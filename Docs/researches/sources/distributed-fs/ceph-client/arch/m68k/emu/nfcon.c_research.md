# sources/distributed-fs/ceph-client/arch/m68k/emu/nfcon.c

Purpose: ARAnyM NatFeat console and tty driver writing to emulator stderr.

Important APIs and data: `stderr_id`, `nfcon_tty_port`, `nfcon_tty_driver`, `nfputs()`, console callbacks `nfcon_write()`/`nfcon_device()`, tty callbacks, `nf_debug_setup()` early parameter handler, `nfcon_init()`, and `nfcon_exit()`.

Control flow and state: `nfputs()` chunks output into a 68-byte stack buffer, null-terminates up to 64 bytes, and calls `NF_STDERR`. `debug=nfcon` can enable/register the console early. Module init obtains the stderr feature, allocates/registers a one-line raw tty driver, links a tty port, and registers the console if not already present. Exit unregisters console and tty resources.

Dependencies and integration: NatFeat base, Linux console and tty layers, early parameter parsing, and ARAnyM `NF_STDERR`.

Risks and test signals: output-only tty has no read path and `write_room()` is fixed at 64. Early console registration depends on NatFeat being callable early. Test `debug=nfcon`, `/dev/nfcon` writes, console handoff, module unload, and behavior when `NF_STDERR` is absent.
