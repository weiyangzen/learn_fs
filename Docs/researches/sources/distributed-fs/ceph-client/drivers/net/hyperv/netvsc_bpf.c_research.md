# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_bpf.c

### Purpose
`netvsc_bpf.c` adds XDP/BPF support to the Hyper-V NetVSC driver. It attaches and detaches XDP programs across NetVSC receive channels, propagates XDP programs to an associated VF when possible, executes XDP on received packets copied from NetVSC RSC state, and implements `ndo_xdp_xmit` by either forwarding to the VF or converting XDP frames into SKBs for synthetic transmit.

### Important APIs, Types, And Functions
Main entry points are `netvsc_run_xdp()`, `netvsc_xdp_get()`, `netvsc_xdp_set()`, `netvsc_vf_setxdp()`, `netvsc_bpf()`, and `netvsc_ndoxdp_xmit()`. `netvsc_xdp_fraglen()` computes aligned SKB fragment requirements. `netvsc_ndoxdp_xmit_fm()` converts one `xdp_frame` into an SKB and sends it through the existing NetVSC transmit path via `netvsc_xdp_xmit()`.

### Control Flow
On receive, `netvsc_run_xdp()` reads the channel's RCU BPF program pointer. If no program is attached, it returns `XDP_PASS`. Otherwise it validates the packet length against MTU plus Ethernet header, allocates a page, prepares an `xdp_buff` with `NETVSC_XDP_HDRM` headroom, copies packet data from `nvchan->rsc`, runs the program, and handles actions. `XDP_PASS` and `XDP_TX` keep the page for later handling; `XDP_REDIRECT` calls `xdp_do_redirect()`, marks the channel for flush, and updates stats; drops and aborted/invalid actions free the page and update or trace error state.

XDP attach uses `netvsc_bpf()` for `XDP_SETUP_PROG`. `netvsc_xdp_set()` rejects MTUs that would exceed a page-backed XDP buffer and rejects LRO, increments program references for all channels, publishes the program to every channel with RCU assignment, and drops old references. If a VF is present, `netvsc_vf_setxdp()` propagates the program through the VF's `ndo_bpf`; failures roll back the synthetic attachment.

`netvsc_ndoxdp_xmit()` first prefers the VF path when the VF is running, carrier is up, netpoll is not active, the VF supports XDP transmit, and the active datapath is VF. Otherwise it selects a synthetic TX queue by CPU, converts frames to SKBs, computes NetVSC hash metadata, records RX queue, calls `netvsc_xdp_xmit()`, and updates XDP TX stats.

### State And Persistence Behavior
Attached programs are stored as RCU pointers in every `netvsc_channel`. Program references are explicitly acquired for additional channels and released on replacement. Per-channel RX stats record XDP drops, redirects, TX, packets, and bytes; TX stats record `xdp_xmit`. There is no persistent storage beyond runtime netdev and channel state.

### Dependencies And Integration Points
The file integrates with Linux XDP core APIs, BPF program reference management, netdevice `ndo_bpf` and `ndo_xdp_xmit`, RCU, VF representor/associated netdev handling from `net_device_context`, NetVSC synthetic transmit helpers, and RNDIS receive state via `nvchan->rsc`.

### Risks
The receive path copies packet data into a newly allocated page for XDP, so allocation failure and MTU/page-size limits are central. Program propagation must keep synthetic and VF state consistent on failure. Reference balancing across multiple channels is sensitive to `nvdev->num_chn`. XDP redirect requires a later flush in `netvsc_poll()`. The fallback XDP transmit path converts frames to SKBs, so performance and ownership semantics differ from native zero-copy XDP.

### Test Signals
Test XDP attach/detach with and without a VF, attach rejection with LRO enabled, MTU too large rejection, channel-count reference handling, XDP actions PASS/DROP/ABORTED/REDIRECT/TX, redirect flush behavior, `ndo_xdp_xmit` VF forwarding and synthetic fallback, netpoll disabling the VF fast path, and teardown while programs are attached.
