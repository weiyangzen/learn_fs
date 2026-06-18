# sources/distributed-fs/ceph-client/drivers/nfc/nfcsim.c

Purpose: Provides a software NFC digital simulator made of two virtual NFC devices connected by paired in-memory links.

Important APIs and functions: Main types are `struct nfcsim` and `struct nfcsim_link`. Link helpers allocate/free links, store SKBs, wake receivers, cancel receives, shut down, and wait for matching frames. Digital ops are `nfcsim_in_configure_hw()`, `nfcsim_in_send_cmd()`, `nfcsim_tg_configure_hw()`, `nfcsim_tg_send_cmd()`, `nfcsim_tg_listen()`, `nfcsim_abort_cmd()`, and `nfcsim_switch_rf()`.

Control flow: Module init creates two links, initializes debugfs, and registers two `nfc_digital_dev` instances with opposite link directions. Sending schedules receive work for the local command and, unless `dropframe` is set, stores the outgoing SKB on the peer link and wakes it after a random 3-10 ms delay. Receive work waits for a frame with matching RF technology and opposite mode, then invokes the digital completion callback. Target listen is modeled as a send with no SKB.

State and persistence: Each device tracks up/down state, initiator/target mode, RF tech, receive timeout, completion callback/context, and debugfs `dropframe`. Each link stores one pending SKB, mode/tech metadata, waitqueue condition, and shutdown flag. Debugfs state is runtime-only.

Dependencies and integration points: Integrates with NFC digital core, debugfs, workqueues, waitqueues, random delay generation, and module init/exit.

Risks: Each link stores only one SKB, so concurrent sends overwrite old pending frames. The wait condition is a simple byte reset after receive, so cancellation and timeout ordering matter. Test signals include two-device DEP exchange, initiator/target mode mismatch, timeout, abort, RF off during receive, debugfs frame drop, module unload during pending work, and shutdown error propagation.
