# sources/distributed-fs/beegfs-go/ctl/internal/bflag/flags.go

Purpose: wraps cobra/pflag options so CTL commands can expose user-friendly flags and translate them into arguments for external BeeGFS command-line tools.

Important APIs/types are `FlagSet`, `NewFlagSet`, `WrappedArgs`, `FlagWrapper`, `baseFlag`, generic `Flag[T]`, `WithEquals`, concrete `stringFlag`, `intFlag`, `boolFlag`, `GlobalFlag`, and `globalFlag`.

Control flow: `NewFlagSet` binds each wrapper to a cobra command. `WrappedArgs` asks each wrapper for target CLI arguments and concatenates non-nil results. Generic `Flag` switches on default value type to create a string/int/bool wrapper. String flags are omitted when empty, int flags are always emitted, bool flags emit only their wrapped flag when true, and `WithEquals` emits `--flag=value` for string/int wrappers. `GlobalFlag` reads values from viper instead of binding a local pflag.

State is each wrapper's pointer to the bound pflag value and static target flag metadata. Global flags read process-wide viper state.

Dependencies include cobra, viper, strconv, and fmt. Integration points are CTL commands that shell out to legacy BeeGFS utilities.

Risks: int flags are always included, so defaults must match target tool expectations. Global bool handling relies on viper type. Generic support is limited to string/int/bool and panics if expanded incorrectly. There are no quoting semantics beyond returning arg slices.

Test signals: no direct tests in this subset.
