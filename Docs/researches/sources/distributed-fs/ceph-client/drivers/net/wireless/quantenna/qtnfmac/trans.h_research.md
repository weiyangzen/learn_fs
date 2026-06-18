## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/trans.h

### Purpose
`trans.h` declares qtnfmac QLINK transport state and public transport functions used by command, event, and bus layers.

### Important APIs, Types, And Functions
It defines command flags and buffer sizing constants, forward-declares `struct qtnf_bus`, and defines `struct qtnf_cmd_ctl_node` plus `struct qtnf_qlink_transport`. It declares `qtnf_trans_init()`, `qtnf_trans_free()`, `qtnf_trans_send_next_cmd()`, `qtnf_trans_handle_rx_ctl_packet()`, and `qtnf_trans_send_cmd_with_resp()`.

### Control Flow
The structures support one current command protected by `resp_lock` and a separate async event queue. Callers initialize transport state during bus bring-up, send commands through the synchronous API, and feed received control skbs into the RX handler.

### State, Persistence, And Dependencies
Transport state is memory-resident and per-bus. Persistent effects are not stored here; packets are passed to bus and event layers. Dependencies include kernel skbuff, module/kernel headers, mutex/spinlock facilities, and QLINK definitions.

### Integration Points
This header is included by qtnfmac command, event, and bus implementations. It is the contract between hardware-specific bus delivery and generic QLINK command/event handling.

### Risks
The declaration of `qtnf_trans_send_next_cmd()` has no implementation in this file subset, so users must rely on other compilation units or avoid it. Single-command state makes external serialization mandatory. Buffer-size constants need to match command builders and bus limits.

### Test Signals
Compile/link coverage for all declared functions, command serialization tests, event queue limit tests, and bus init/free ordering exercise this interface.
