# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.c

Purpose: Creative 20K1 chip-specific implementation of the ctxfi `struct hw` abstraction. It translates generic SRC, SRCIMP, AMIXER, DAI/DAO, timer, PLL, GPIO, I2C, transport, interrupt, and card lifecycle operations into 20K1 register writes.

Important APIs and types: `struct hw20k1` embeds `struct hw` and register locks. Control-block types mirror hardware state for SRC, SRC manager, SRCIMP manager, AMIXER, DAI, DAO, and DAIO manager. Public factory/destructor are `create_20k1_hw_obj` and `destroy_20k1_hw_obj`; `ct20k1_preset` fills the operation table.

Control flow: setters update software control blocks and dirty bits. Commit functions write only dirty fields to indirect 20K1 registers. `hw_card_init` enables PCI, handles UAA-to-X-Fi switch for CTUAA, requests regions/IRQ, initializes PLL and auto-init, enables audio ring/global control, clears interrupts, configures GPIO by model, initializes transport VM page table, DAIO, DAC, ADC, and SRC audio-ring input. Interrupt handler reads `GIP`, invokes `hw->irq_callback`, acknowledges status.

State and persistence: runtime state includes I/O base, IRQ, model-specific GPIO/I2C programming, dirty control blocks, and spinlocks for indirect 20K1 and PCI register windows. PM suspend stops transport/PLL and may switch CTUAA config space; resume reruns card init.

Dependencies and integration: depends on `ct20k1reg.h`, Linux PCI/I/O/IRQ/delay, and the generic resource managers calling the `struct hw` table. DAC/ADC setup uses GPIO and PCI indirect I2C access.

Risks and test signals: busy-wait loops poll hardware without long timeout in several I2C/SRC paths; UAA mode switching rewrites PCI config space; teardown must free IRQ, unmap memory, release regions, and disable PCI exactly once. Tests: 20K1 probe/init on each model quirk, playback/capture/S/PDIF, ADC source selection, timer interrupt callback, suspend/resume, CTUAA UAA switch, and resource-manager dirty commit correctness.
