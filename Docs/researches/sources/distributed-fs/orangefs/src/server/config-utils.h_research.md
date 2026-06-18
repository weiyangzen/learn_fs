# sources/distributed-fs/orangefs/src/server/config-utils.h

## Purpose
Declares the process-global server-configuration accessor functions implemented by `config-utils.c`.

## Important APIs, Types, And Functions
The header forward-declares `struct server_configuration_s` usage through the prototypes `PINT_get_server_config(void)` and `PINT_set_server_config(struct server_configuration_s *cfg_p)`.

## Control Flow
No control flow is implemented. Callers include this header when they need to publish or retrieve the active server configuration pointer.

## State And Persistence
The header stores no state; it exposes access to a global pointer managed by the implementation.

## Dependencies And Integration Points
It avoids including the full server-configuration definition, which keeps dependency weight low for consumers that only pass pointers. It must stay in sync with `config-utils.c` and the actual configuration type name.

## Risks And Test Signals
The risk is mostly API misuse: callers can retrieve NULL before initialization or keep using a pointer after owner cleanup. Build coverage and startup tests that initialize configuration before dependent modules run are the practical signals.
