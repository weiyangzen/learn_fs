
# sources/distributed-fs/ceph-client/drivers/soc/gemini/soc-gemini.c

## Purpose
Early Gemini SoC setup that identifies Cortina Gemini hardware and configures BUS2 backplane arbitration defaults through a syscon regmap.

## Important APIs, Types, and Functions
- `gemini_soc_init()` is registered with `subsys_initcall()`.
- Register constants define global ID and arbitration control fields, default burst size, and default high-priority GMAC bits.

## Control Flow
At subsys init, the function returns immediately unless the root compatible is `cortina,gemini`. It looks up `cortina,gemini-syscon`, reads the global word ID, builds the default arbitration value, updates burst/priority fields in `GEMINI_GLOBAL_ARB1_CTRL`, logs SoC/revision/arbitration, and returns.

## State and Persistence
State is only syscon register configuration. It persists until hardware reset or another driver changes it.

## Dependencies and Integration Points
Depends on OF machine compatible, MFD syscon/regmap, and Gemini syscon DT node.

## Risks
Missing syscon returns an initcall error. Arbitration policy is hard-coded to GMAC priority and burst size, so platform-specific tuning requires code or DT changes.

## Test Signals
Boot on Gemini and non-Gemini systems, syscon lookup failure, regmap read/update failure, and verification of final arbitration register bits.
