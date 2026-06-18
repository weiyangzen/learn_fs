# sources/distributed-fs/ceph-client/include/net/nfc/digital.h

Purpose: declares the NFC Digital Protocol stack driver-facing interface for initiator and target mode RF framing, command exchange, polling, NFC-DEP state, and CRC handling.

Important APIs and types: RF/framing enums define hardware configuration values. `struct digital_tg_mdaa_params` carries automatic anti-collision listen-mode responses. `struct nfc_digital_ops` supplies synchronous configure hooks and asynchronous send/listen hooks. `struct nfc_digital_dev` stores the backing `nfc_dev`, supported protocols, headroom/tailroom, poll technology rotation, command queues, delayed polling, NFC-DEP counters, payload limits, CRC helpers, and driver data. Allocation/registration/free helpers wrap the stack lifecycle.

Control flow: drivers allocate/register a digital device with ops, the stack configures RF technology and framing, queues serialized commands, and requires each asynchronous op to complete through `nfc_digital_cmd_complete_t`, including timeout/error responses as `ERR_PTR()`.

State and persistence: runtime state is in-memory only: current protocol/RF tech, DEP PNI/DID/RWT, chained skb, command queue, saved skb, and polling index. No durable device state is stored.

Dependencies and integration points: integrates with `net/nfc/nfc.h`, `sk_buff`, workqueues, mutexes, and NFC core target/data-exchange APIs.

Risks and test signals: high-risk behavior is missing async completion, wrong timeout handling, CRC ownership mismatch, and target-mode RF detection errors. Test initiator polling, target listen/listen_mdaa/listen_md, aborts, timeout callbacks, CRC-capability matrices, chaining, and unregister with queued work.
