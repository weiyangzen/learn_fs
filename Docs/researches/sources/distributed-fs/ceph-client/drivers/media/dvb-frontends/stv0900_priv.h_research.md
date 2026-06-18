# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv0900_priv.h

### Purpose
`stv0900_priv.h` is the private type and helper contract for the STV0900 driver. It defines driver-local enums, search/result/internal state structures, utility macros, debug printing, and prototypes shared across the core and algorithm implementation files.

### Important APIs, Types, And Functions
Utility macros include `INRANGE`, `MAKEWORD`, `LSB`, `MSB`, boolean constants, and `dprintk()`. Lookup support is defined by `struct stv000_lookpoint` and `struct stv0900_table`. Enums describe error codes, TS clock modes, acquisition states, LDPC/demod modes, signal-presence states, demod path numbers, tracking/search standards, search algorithms, modulation, DVB-S2 modcodes, FEC, frame length, pilots, rolloff, IQ inversion/search policy, DiSEqC mode, and single/dual demod mode. `struct stv0900_init_params`, `struct stv0900_search_params`, `struct stv0900_signal_info`, `struct stv0900_internal`, and `struct stv0900_state` are the main state carriers. Prototypes expose register access, lock checking, signal search, tuner control, carrier-loop lookup, modcod control, standard detection, auto-tuner frequency access, and debug state.

### Control Flow
The header has no executable control flow, but it defines the states consumed by the search algorithm and frontend callbacks. A typical flow is: board attach builds `stv0900_init_params`; initialization fills `struct stv0900_internal`; tuning fills per-demod search fields and calls `stv0900_algo()`; the algorithm updates `struct stv0900_signal_info`; status/metric callbacks read those results and hardware state.

### State, Persistence, And Dependencies
`struct stv0900_internal` is the shared persistent chip state for one physical STV0900: clocks, rolloff, demod mode, per-demod tuning/search parameters, tuner type, result/error arrays, I2C adapter/address, clock mode, chip id, TS config, aggregate error state, and demod reference count. `struct stv0900_state` is per frontend and holds the shared internal pointer, I2C adapter, board config, embedded `dvb_frontend`, and demod index. The header depends on Linux I2C types and on public `stv0900.h` types being available through includers.

### Integration Points
This file connects `stv0900_core.c` with other STV0900 implementation units, especially the acquisition algorithm source that provides `stv0900_algo()`, `stv0900_check_signal_presence()`, and `stv0900_get_standard()`. It also codifies the contract with register labels from `stv0900_reg.h`: helpers take encoded labels and demod-specific code selects path-specific aliases. The DVB core sees only the public frontend object, while these private structures hold the implementation details.

### Risks
Enums and array indices must remain aligned: many internal arrays are size two and indexed by `enum fe_stv0900_demod_num`. Any invalid demod value can corrupt memory. The `TRUE`/`FALSE` macros and broad debug macro are legacy style and can mask type issues. The shared internal structure is mutable across both frontend paths, so algorithm code must avoid overwriting the other path's settings except for intentional single/dual LDPC changes. Function prototypes imply cross-file coupling; signature drift or mismatched enum semantics would break acquisition behavior.

### Test Signals
Compile coverage across all STV0900 translation units is the first signal. Runtime signals include correct per-demod isolation in dual mode, correct single-mode LDPC switching, valid search state transitions, sane result fields after lock, correct I2C register helper behavior for encoded labels, and debug logging that identifies search/lock failures without changing behavior when disabled.
