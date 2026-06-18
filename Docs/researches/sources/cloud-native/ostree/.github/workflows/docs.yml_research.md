<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/docs.yml -->
## sources/cloud-native/ostree/.github/workflows/docs.yml

### Purpose
This workflow builds API documentation, manpage HTML, Jekyll docs, and deploys GitHub Pages for non-PR runs.

### APIs, Types, and Control Flow
The `build` job runs inside the FCOS buildroot container, checks out the repo, marks it safe for git, installs dependencies, runs `./autogen.sh --enable-gtk-doc --enable-man --enable-man-html`, builds `apidoc` and `manhtml`, copies generated docs with `docs/prep-docs.sh`, builds the Jekyll site, and uploads a Pages artifact. The `deploy` job depends on `build`, skips PRs, requests Pages/id-token permissions, and calls `actions/deploy-pages`.

### State, Dependencies, and Integration
Outputs are `docs/_site` and GitHub Pages artifacts. Integration spans autotools, gtk-doc, XSLT manpage generation, Jekyll, and Pages deployment. Concurrency separates PR artifact names from production deploy artifacts.

### Risks and Test Signals
Docs build depends on buildroot image contents and gtk-doc/man tooling. PR artifacts are not deployed, limiting accidental publication. Test signal is successful build and Pages deployment URL for main branch runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/docs.yml -->
