# sources/distributed-fs/ceph-client/arch/sparc/kernel/starfire.c

Purpose: detects Sun Enterprise Starfire/E10000 systems and translates interrupt map entries to Starfire-specific extended UPA interrupt delivery registers.

Important APIs/types/functions: global `this_is_starfire`, `check_if_starfire()`, `starfire_hookup()`, `starfire_translate()`, and `struct starfire_irqinfo` track per-UPAID translation registers and IMAP slots.

Control flow: detection looks for `/ssp-serial`. Hookup allocates an IRQ info record for a UPAID, computes the hardware MID and translation register base, initializes 32 slots, and marks already-programmed registers as reserved. Translation locates the info record by IMAP bus MID, reuses or allocates a slot for the IMAP, maps the requested logical UPAID to real Starfire form, writes the translation register, and returns the slot index.

State and persistence: `sflist` stores runtime translation slots; hardware translation registers are programmed. No disk persistence.

Dependencies and integration points: integrates with sparc64 IRQ delivery, UPA register access, PROM probing, and Starfire checks in SMP mondo delivery.

Risks: allocation failure or missing board records halt/panic because interrupt delivery would be unreliable. Slot exhaustion indicates inconsistent IMAP handling. Existing register contents are preserved defensively.

Test signals: Starfire boot detection, IRQ routing for devices behind multiple boards, preservation of firmware mappings, and non-Starfire systems leaving `this_is_starfire` clear.
