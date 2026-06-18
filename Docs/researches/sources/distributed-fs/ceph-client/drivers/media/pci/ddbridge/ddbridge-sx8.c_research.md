# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-sx8.c

Purpose: implements the DVB frontend behavior for Digital Devices MAX SX8 MCI hardware. It allocates tuners/demods, starts DVB-S/S2/S2X searches, handles IQ modes, reports status/strength/CNR, and exports an `mci_cfg` used by `ddbridge-max.c`.

Important APIs/types/functions: `struct sx8_base` extends `mci_base` with tuner use counts, gain modes, LDPC bitrate accounting, demod use bitmap, IQ mode, burst size, and direct mode. `struct sx8` extends `mci` with lock/start state and last signal info. Key ops are `set_parameters()`, `start()`, `start_iq()`, `stop()`, `read_status()`, `tune()`, `set_input()`, and `release()`. `ddb_max_sx8_cfg` supplies ops and sizes.

Control flow: tuning stops any previous search, derives IQ mode from stream ID, chooses TS config, reserves a demod and LDPC budget under `tuner_lock`, enables tuner input, sends MCI search or IQ commands, then polling reads status and signal info. Stop sends MCI stop, disables IQ output, releases tuner/demod accounting, and restores normal TS config.

State and persistence: shared base state tracks all active SX8 frontends on the link. Per-frontend state tracks selected tuner/demod, started flag, and signal cache. No durable persistence.

Dependencies/integration: depends on MCI command API, ddbridge MMIO helpers, DVB frontend property cache, and MAX attach wrapper for LNB operations.

Risks and test signals: demod allocation and LDPC bitrate limits can reject valid workloads or oversubscribe firmware; IQ mode excludes other demods; release must balance shared base count. Test concurrent multi-tuner tuning, high-symbol-rate transponders, multistream stream IDs, IQ modes, stop/re-tune loops, signal stat reads, and module unload after multiple frontends.
