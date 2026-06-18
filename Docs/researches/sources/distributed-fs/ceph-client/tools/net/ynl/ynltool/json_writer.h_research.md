# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/json_writer.h

Purpose: public header for the `ynltool` streaming JSON writer. It exposes an opaque `json_writer_t` and the functions implemented in `json_writer.c`.

Important APIs/types: declares lifecycle (`jsonw_new`, `jsonw_destroy`), formatting (`jsonw_pretty`, `jsonw_reset`), object names (`jsonw_name`), primitive emitters, field helpers, and collection delimiters. `format(printf)` attributes are applied to printf-style functions to catch format mismatches at compile time.

State/dependencies: no state in the header beyond the opaque typedef. Includes standard bool, integer, varargs, and stdio headers. A `jsonw_err_handler_fn` typedef is declared but not used by the implementation in this subset.

Integration: included by `main.h`, which makes JSON writer globals available to ynltool subcommands.

Risks/test signals: header and implementation must remain synchronized; missing prototypes would be caught by `-Wmissing-prototypes`/`-Werror` build settings. JSON validity is tested through consumers of the API rather than the header itself.
