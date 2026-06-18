# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/fsl_qe_udc.h

## Purpose

`fsl_qe_udc.h` is the private hardware and state header for the Freescale QE/CPM USB device controller driver. It defines controller register bits, endpoint parameter RAM layouts, frame metadata, request/endpoint/controller structures, EP0 state constants, transfer modes, and QE/CPM buffer descriptor status bits used by `fsl_qe_udc.c`.

## Important APIs, Types, And Constants

Top-level constants describe hardware capabilities and allocation sizes: four endpoints, EP0 max packet 64, RX rings up to 256 BDs, TX rings 16 BDs, and `MIN_EMPTY_BDS` for RX NACK pressure. Register masks cover USB mode, endpoint fields, command bits, event/mask bits, frame number masks, and bus mode fields.

`struct usb_device_para` and `struct usb_ep_para` model QE/CPM USB parameter RAM. They hold endpoint parameter pointers, RX/TX state, frame counters, BD bases/pointers, max receive buffer length, CRC/temp fields, and transaction counters. `struct qe_frame` is the driver's abstract RX/TX frame. Inline helpers reset and initialize it.

`struct qe_req` wraps `struct usb_request` with a queue node, owning endpoint pointer, and mapped flag. `struct qe_ep` wraps `struct usb_ep` and stores queue, controller/gadget pointers, endpoint state, RX/TX BD ring pointers, RX/TX frames and buffers, active TX request accounting, direction, transfer mode, data toggle, tasklet/setup flags, DMA metadata, local NACK state, and endpoint name. `struct qe_udc` stores the gadget object, gadget driver, endpoint array, EP0 setup buffer, spinlock, SoC type, parameter RAM pointers, USB state, EP0 state/direction, buffers, IRQ/register pointers, RX tasklet, and removal completion.

Buffer descriptor flags define ownership, wrap, interrupt, last, CRC, PID, and error bits for TX and RX. CPM command constants define stop/restart transmit opcodes.

## Control Flow And State

This header defines the state machine used by the C file. EP0 progresses through wait-for-setup, transmit data, need-ZLP, wait-for-OUT-status, and receive data states. Endpoint state is idle, NACK, or stall. RX/TX data toggle is stored in `qe_ep.data01` and converted into PID bits in BDs and frame info. Request queue state lives in `qe_ep.queue`, while one active IN request can be tracked as `qe_ep.tx_req` with `sent` and `last` counters.

Persistence is volatile. BD rings and endpoint parameter RAM reside in QE/CPM MURAM for the lifetime of endpoint/controller setup. No state is durable across driver unload or hardware reset.

## Dependencies And Integration Points

The header depends on Linux USB gadget types, list heads, DMA addresses, timer/tasklet-capable kernel infrastructure, and QE/CPM BD definitions from platform headers. It is tightly coupled to `struct usb_ctlr` register layout from Freescale QE/CPM platform headers. The generic UDC core sees only generic gadget objects; all other types are private.

## Risks

Risks center on bit-level hardware correctness. BD status words overlay status and length fields, so masks must match the platform definition. RX buffer sizing includes CRC and alignment slop. `ep_index()` assumes `ep.desc` exists. `ep_is_in()` treats EP0 direction specially through `udc->ep0_dir`, making EP0 direction critical for DMA mapping and completion. Structure padding or type changes can break hardware behavior.

## Test Signals

Runtime signals include correct EP0 setup parsing, data toggle progression, RX NACK/normal transitions, TX and RX BD ownership cycling, endpoint halt state reflected in `usb_usep`, and clean allocation/free of MURAM parameter blocks and BD rings. Stress tests should watch ring wrap, RX BD exhaustion, and request completion statuses after reset or dequeue.
