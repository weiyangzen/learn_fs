# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-btcvsd.c

## Purpose
Implements MediaTek BTCVSD/MSBC ALSA PCM support, bridging PCM read/write operations to Bluetooth firmware SRAM packet buffers for SCO audio.

## Important APIs, Types, And Functions
Core state is `struct mtk_btcvsd_snd` with TX/RX stream objects, IRQ, infra regmap, BT packet/control register pointers, SRAM bases, locks, wait queues, and packet buffers. Important functions include state control `mtk_btcvsd_snd_set_state()`, transfer helpers, SRAM read/write functions, IRQ handler `mtk_btcvsd_snd_irq_handler()`, wait helper `wait_for_bt_irq()`, PCM copy/read/write/pointer/open/close/hw_params/hw_free/prepare/trigger callbacks, kcontrols for band/loopback/mute/IRQ/timeout/timestamps, and probe/remove.

## Control Flow, State, And Persistence
Probe allocates TX/RX streams, initializes locks and queues, requests the IRQ, maps BT packet and SRAM regions with `of_iomap()`, reads infra and offset properties, derives packet register pointers, disables IRQs while idle, and registers a component without DAIs. Playback writes packetized user data into a circular TX buffer; interrupts move packets to BT SRAM when firmware requests them. Capture interrupts read BT SRAM into a circular RX buffer, and userspace reads from it. State transitions enable or disable IRQs depending on TX/RX activity.

## Dependencies And Integration Points
Depends on DT compatible `mediatek,mtk-btcvsd-snd`, `mediatek,infracfg`, `mediatek,offset`, low-trigger IRQ, BT firmware SRAM layout, ASoC component PCM callbacks, and ALSA controls.

## Risks And Test Signals
Risks include direct `u32 *` MMIO access instead of readl/writel, pointer casts to SRAM addresses, packet counter wrap arithmetic, unbounded `num_valid_addr` growth versus fixed 20-entry array, wait timeouts returning partial transfers, lock coverage around shared counters, and manual iounmap paths. Test signals include NB/WB SCO loopback, TX mute cleaning, RX overflow/TX underflow logs, timeout controls, timestamp controls, suspend-like BT sleep returning `0xdeadfeed`, and stress with concurrent playback/capture.
