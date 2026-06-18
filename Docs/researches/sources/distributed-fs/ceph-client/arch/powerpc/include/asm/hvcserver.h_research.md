# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcserver.h

Purpose: Declares PPC64 hypervisor virtual-console server partner discovery and connection management interfaces.

Important APIs, types, and functions: `HVCS_CLC_LENGTH` sets the converged location code length. `struct hvcs_partner_info` records list linkage, partner unit address, partition ID, and location code. APIs include `hvcs_get_partner_info()`, `hvcs_free_partner_info()`, `hvcs_register_connection()`, and `hvcs_free_connection()`.

Control flow: Server code requests partner info into a list, registers a connection to a partner partition/unit address, later frees the connection and list data.

State and persistence: Partner lists are caller-owned kernel memory. Active connection state is managed by firmware and the hvcs driver.

Dependencies and integration points: Depends on Linux lists and pSeries VIO/hvcs firmware calls.

Risks: Location-code lengths and caller-provided `pi_buff` storage must match firmware output. Connection registration/freeing must be balanced to avoid stale virtual terminal routes.

Test signals: Partner enumeration with multiple entries, long location codes, connection register/free cycles, firmware errors, and list cleanup after partial failures.
