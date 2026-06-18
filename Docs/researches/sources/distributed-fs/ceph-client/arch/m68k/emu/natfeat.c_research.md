# sources/distributed-fs/ceph-client/arch/m68k/emu/natfeat.c

Purpose: ARAnyM Native Features base support. It discovers emulator-provided services, exports the call interface, prints to emulator stderr, and registers emulator poweroff.

Important APIs and functions: assembly stubs `nf_get_id_phys` and exported `nf_call`; `nf_get_id()` copies feature names to a physical-addressable stack buffer; `nfprint()` formats to a static buffer and calls `NF_STDERR`; `nf_poweroff()` calls `NF_SHUTDOWN`; `nf_init()` probes `NF_VERSION`/`NF_NAME` and registers poweroff.

Control flow and state: NatFeat opcodes `.short 0x7300` and `.short 0x7301` are wrapped with exception-table fallback to return zero when unsupported. `nf_init()` logs the emulator name/version only when features exist. State is minimal: no persistent storage, only a static print buffer and registered poweroff hook.

Dependencies and integration: ARAnyM emulator ABI, `virt_to_phys`, exception tables, Linux reboot/poweroff registration, and optional nfblock/nfcon/nfeth modules.

Risks and test signals: `nfprint()` uses a static buffer and is not reentrant. Feature names over 31 bytes return no ID. Test on ARAnyM with NatFeat enabled/disabled, verify exception fallback, feature lookup, stderr output, and poweroff.
