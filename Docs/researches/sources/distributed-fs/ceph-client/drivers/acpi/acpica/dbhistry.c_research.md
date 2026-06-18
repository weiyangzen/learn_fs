# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dbhistry.c

## Purpose
Implements the AML debugger command history ring buffer and history recall commands.

## Important APIs And Functions
The module defines `HISTORY_SIZE` as 40 and stores `HISTORY_INFO` entries containing a heap-allocated command string plus command number. `acpi_db_add_to_history` inserts a non-empty command, reuses or reallocates the target slot as needed, stores `acpi_gbl_next_cmd_num`, advances circular indices, and caps count at 40. `acpi_db_display_history` prints commands from the oldest index. `acpi_db_get_from_history` resolves a supplied command number or defaults to the previous command. `acpi_db_get_history_by_index` searches the circular buffer and returns the stored command pointer.

## Control Flow, State, And Persistence
History state is process-local static memory: `acpi_gbl_history_buffer`, `acpi_gbl_lo_history`, `acpi_gbl_num_history`, and `acpi_gbl_next_history_index`. Command numbers persist monotonically through the debugger session via `acpi_gbl_next_cmd_num`. Recalled commands are not copied; callers dispatch the returned stored pointer.

## Dependencies And Integration Points
Used by `dbinput.c` for `History`, `!`, and `!!`. It uses ACPICA OS allocation/free and output services. `dbinput.c` deliberately avoids adding `!!` itself to history to prevent recursive repeat loops.

## Risks And Test Signals
Risks include unchecked allocation failure before `strcpy`, fixed-size history eviction behavior, returned command pointers being overwritten by later history insertion, and the final invalid-history message printing the circular index rather than requested command number. Test signals include command history wraparound beyond 40 entries, recalling explicit and last commands, repeated `!!`, long commands that force reallocation, and allocation-failure injection.
