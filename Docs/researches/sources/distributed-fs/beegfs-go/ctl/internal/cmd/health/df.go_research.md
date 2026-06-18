
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/df.go

- Purpose: implements `health capacity` alias `df` for metadata and storage target capacity.
- Important APIs: `newDFCmd` and `printDF`.
- Control flow/state: gets all targets, splits meta versus storage, sorts each by target numeric ID, prints headings, and delegates table rendering to `target.PrintTargetList`.
- Dependencies/integration: depends on `ctl/pkg/ctl/target.GetTargets`, target frontend print config, and BeeGFS node type constants.
- Risks/tests: no local persistence; output ordering depends on stable numeric sort. `<=` in sort comparator is unusual because Go sort expects strict less. No direct tests found.
