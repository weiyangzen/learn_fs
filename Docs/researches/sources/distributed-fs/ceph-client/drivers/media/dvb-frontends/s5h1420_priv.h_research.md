# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/s5h1420_priv.h

Purpose: Private symbolic register map for S5H1420/PN1010.

Important APIs/types/functions: `enum s5h1420_register` names demod control, PLL, QPSK, loop, NCO, monitor, FEC, Viterbi, sync, MPEG, DiSEqC, RF, and error registers used by `s5h1420.c`.

Control flow: C code uses these constants in tuning, status, DiSEqC, and output configuration instead of raw numeric addresses.

State and persistence: no state; symbolic constants only.

Dependencies/integration: includes `asm/types.h`.

Risks: constants must match silicon documentation; enum names cover only low register range used by the driver, while raw addresses still appear in code.

Test signals: compile coverage plus functional tests of every code path that touches PLL, DiSEqC, MPEG, and Viterbi registers.
