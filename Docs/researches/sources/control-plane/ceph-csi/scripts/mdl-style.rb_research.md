<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/mdl-style.rb -->
## sources/control-plane/ceph-csi/scripts/mdl-style.rb

Purpose: markdownlint style configuration.

Behavior: starts from `all`, sets MD013 line length to 80 while ignoring code blocks and tables, and excludes inline HTML, missing fenced code language, and first-line top-level header rules.

State and dependencies: consumed by `mdl` from `lint-extras.sh`.

Integration points: keeps Markdown linting compatible with GitHub-flavored docs and repository conventions.

Risks: excluded rules allow HTML and untyped fences, which may reduce documentation consistency but avoids noisy failures.

Test signals: lint CI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/mdl-style.rb -->
