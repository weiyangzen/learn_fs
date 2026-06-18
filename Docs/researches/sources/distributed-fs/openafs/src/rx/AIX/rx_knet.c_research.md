# sources/distributed-fs/openafs/src/rx/AIX/rx_knet.c

Purpose: AIX Rx kernel network integration, intercepting UDP input for registered Rx ports, raising Rx timer events, and sending packets through kernel mbuf/socket APIs.

Important APIs/types/functions: `rxk_init`, `shutdown_rxkernel`, `rxk_input`, `rxk_kpork`, `rxk_RX_input`, `rxk_isr`, `rxk_fasttimo`, `ip_stripoptions`, and `osi_NetSend`.

Control flow: `rxk_init` finds the UDP protocol switch, wraps `pr_input` and `pr_fasttimo`, and registers a pseudo input type. Incoming UDP packets on Rx ports are queued to the network kproc, stripped/validated/checksummed, converted from mbufs to Rx packets, and delivered through `rxk_PacketArrivalProc`; other packets fall through to original UDP input. Send path copies iovecs into an mbuf chain and invokes `PRU_SEND`.

State/persistence: persists `parent_proto`, `rxk_q`, fake `rxk_bogosity`, `rxk_initDone`, `rxk_ports`, and `rxk_portRocks`.

Dependencies/integration: AIX mbufs, protosw, netisr/input-type hooks, `rx_kcommon`, Rx packet alloc/arrival hooks, and `rxevent_RaiseEvents`.

Risks: protocol-switch patching is invasive; mbuf header manipulation and checksum rewriting are fragile; send path copies because queued mbufs outlive caller buffers; shutdown must restore UDP hooks and close per-port sockets. Test signals include AIX kernel build, UDP pass-through, Rx receive/send, checksummed packets, IP options, and unload/reload cycles.
