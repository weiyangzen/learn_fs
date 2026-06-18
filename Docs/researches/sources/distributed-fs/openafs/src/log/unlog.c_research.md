## sources/distributed-fs/openafs/src/log/unlog.c

Purpose: Implements `unlog`, removing all tokens or selected cell tokens from the cache manager.

Important APIs and functions: Command entry is `CommandProc` via the OpenAFS cmd package. `main` creates syntax with optional `-cell` list. Helpers are `unlog_ForgetCertainTokens`, `unlog_NormalizeCellNames`, `unlog_CheckUnlogList`, and `unlog_VerifyUnlog`.

Control flow: Without `-cell`, it calls `ktc_ForgetAllTokens`. With cells, it accepts up to 20 names, normalizes each through client cell configuration, lists and saves all current token sets, marks matching cells for deletion, warns for requested cells without tokens, forgets all tokens, then re-registers the token sets not marked deleted.

State and persistence: Mutates cache manager token state. Allocates normalized cell names and token set arrays; some allocations intentionally live until process exit.

Dependencies and integration: Uses OpenAFS cmd, auth/cellconfig/util/token/ktc libraries. Built by `src/log/Makefile.in`.

Risks: Selective deletion is not atomic from the cache manager perspective; there is a window where all tokens are removed before preserved tokens are restored. `MAXCELLS` is fixed at 20. Memory for normalized names and token sets is not fully released before exit. Restoration failures are reported but do not roll back.

Test signals: No-argument remove-all, one cell, multiple cells, unknown cell normalization, requested cell with no token warning, restoration failure, and concurrent token changes during selective unlog.
